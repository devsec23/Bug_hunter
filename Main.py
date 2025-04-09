import os
import subprocess

# دالة لتحميل وتثبيت الأدوات إذا لم تكن موجودة
def install_tool(tool_name, install_command):
    try:
        # تحقق إذا كانت الأداة موجودة
        result = subprocess.run(f"which {tool_name}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            print(f"[!] {tool_name} not found, installing...")
            subprocess.run(install_command, shell=True)
        else:
            print(f"[+] {tool_name} is already installed.")
    except Exception as e:
        print(f"[!] Error installing {tool_name}: {str(e)}")

# دالة لتحميل Wordlists
def download_wordlists():
    wordlist_url = "https://github.com/danielmiessler/SecLists/archive/master.zip"
    try:
        if not os.path.exists("SecLists-master"):
            print("[*] Downloading SecLists Wordlists...")
            subprocess.run(f"wget {wordlist_url} -O SecLists.zip", shell=True)
            subprocess.run("unzip SecLists.zip", shell=True)
            print("[+] SecLists Wordlists downloaded and extracted.")
        else:
            print("[+] Wordlists already downloaded.")
    except Exception as e:
        print(f"[!] Error downloading Wordlists: {str(e)}")

# دالة لتثبيت الأدوات
def install_required_tools():
    tools = {
        "dirsearch": "git clone https://github.com/maurosoria/dirsearch.git",
        "nikto": "apt-get install nikto -y",
        "gobuster": "apt-get install gobuster -y",
        "ffuf": "apt-get install ffuf -y",
        "arachni": "gem install arachni",
        "subfinder": "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "amass": "go install github.com/OWASP/Amass/v3@latest"
    }
    
    for tool, command in tools.items():
        install_tool(tool, command)

# دالة لتشغيل الأداة
def run_tool(command, output_file):
    try:
        print(f"[*] Running {command}")
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(output_file, "w") as f:
            f.write(result.stdout.decode())
        print(f"[*] Results saved to {output_file}")
    except Exception as e:
        print(f"[!] Error: {str(e)}")

# دالة لفحص الأدوات واستخدامها
def run_scans(domain):
    print(f"[*] Running scans for {domain}")

    # استخدام Subfinder
    subfinder_command = f"subfinder -d {domain} -o results/subfinder.txt"
    run_tool(subfinder_command, "results/subfinder.txt")

    # استخدام Amass
    amass_command = f"amass enum -d {domain} -o results/amass.txt"
    run_tool(amass_command, "results/amass.txt")

    # دمج النتائج من الأدوات
    with open("results/final_subdomains.txt", "w") as final_file:
        with open("results/subfinder.txt", "r") as f:
            final_file.write(f.read())
        with open("results/amass.txt", "r") as f:
            final_file.write(f.read())

    # استخدام Dirsearch
    dirsearch_command = f"python3 dirsearch/dirsearch.py -u http://{domain} -w SecLists-master/Discovery/Web-Content/common.txt -o results/dirsearch.txt"
    run_tool(dirsearch_command, "results/dirsearch.txt")

    # استخدام Gobuster
    gobuster_command = f"gobuster dir -u http://{domain} -w SecLists-master/Discovery/Web-Content/common.txt -o results/gobuster.txt"
    run_tool(gobuster_command, "results/gobuster.txt")

    # استخدام FFUF
    ffuf_command = f"ffuf -u http://{domain}/FUZZ -w SecLists-master/Discovery/Web-Content/common.txt -o results/ffuf.txt"
    run_tool(ffuf_command, "results/ffuf.txt")

    # استخدام Nikto
    nikto_command = f"nikto -h http://{domain} -o results/nikto.txt"
    run_tool(nikto_command, "results/nikto.txt")

    # استخدام Arachni
    arachni_command = f"arachni http://{domain} --output-dir=results/arachni"
    run_tool(arachni_command, "results/arachni.txt")

    print(f"[*] Scans completed for {domain}")

# الدالة الرئيسية لتشغيل الأداة
def main():
    # تثبيت الأدوات المطلوبة
    install_required_tools()

    # تحميل Wordlists
    download_wordlists()

    # طلب إدخال النطاق المستهدف من المستخدم
    domain = input("Enter the target domain (e.g., defense.tn): ")
    
    # إنشاء مجلد لتخزين النتائج
    os.makedirs("results", exist_ok=True)

    # تشغيل فحص الأدوات
    run_scans(domain)

if __name__ == "__main__":
    main()
