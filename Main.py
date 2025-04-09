import os
import subprocess
import sys

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

# دالة لتشغيل الأدوات
def run_tool(command, output_file):
    try:
        print(f"[*] Running {command}")
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(output_file, "w") as f:
            f.write(result.stdout.decode())
        print(f"[*] Results saved to {output_file}")
    except Exception as e:
        print(f"[!] Error: {str(e)}")

# تثبيت الأدوات الضرورية
def install_required_tools():
    tools = {
        "subfinder": "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "amass": "go install github.com/OWASP/Amass/v3@latest",
        "sqlmap": "git clone https://github.com/sqlmapproject/sqlmap.git && cd sqlmap && pip install -r requirements.txt",
        "nikto": "apt-get install nikto",
        "arachni": "gem install arachni"
    }
    
    for tool, command in tools.items():
        install_tool(tool, command)

# فحص subdomains المكتشفة
def scan_subdomains(domain):
    print(f"[*] Scanning subdomains for {domain}")

    # تشغيل أدوات اكتشاف النطاقات الفرعية
    subfinder_command = f"subfinder -d {domain} -o results/subfinder.txt"
    amass_command = f"amass enum -d {domain} -o results/amass.txt"
    run_tool(subfinder_command, "results/subfinder.txt")
    run_tool(amass_command, "results/amass.txt")

    # دمج النطاقات الفرعية
    with open("results/final_subdomains.txt", "w") as final_file:
        with open("results/subfinder.txt", "r") as f:
            final_file.write(f.read())
        with open("results/amass.txt", "r") as f:
            final_file.write(f.read())

    print(f"[*] Finished scanning subdomains for {domain}")

# فحص الثغرات على كل subdomain
def scan_vulnerabilities():
    with open("results/final_subdomains.txt", "r") as f:
        subdomains = f.readlines()

    for subdomain in subdomains:
        subdomain = subdomain.strip()
        print(f"[*] Scanning {subdomain} for vulnerabilities...")

        # فحص SQLi باستخدام SQLmap
        sqlmap_command = f"sqlmap -u http://{subdomain} --batch --output-dir=results/sqlmap/{subdomain}"
        run_tool(sqlmap_command, f"results/sqlmap/{subdomain}.txt")

        # فحص XSS باستخدام Arachni
        arachni_command = f"arachni http://{subdomain} --output-dir=results/arachni/{subdomain} --report-save-file=results/arachni/{subdomain}_report.afr"
        run_tool(arachni_command, f"results/arachni/{subdomain}_report.afr")

        # فحص التكوينات غير الآمنة باستخدام Nikto
        nikto_command = f"nikto -h http://{subdomain} -o results/nikto/{subdomain}_config.txt"
        run_tool(nikto_command, f"results/nikto/{subdomain}_config.txt")

        print(f"[*] Finished scanning {subdomain}.")

# دمج جميع النتائج في تقرير واحد
def generate_report():
    with open("results/final_report.txt", "w") as final_report:
        for folder in os.listdir("results"):
            folder_path = os.path.join("results", folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    with open(os.path.join(folder_path, file), "r") as f:
                        final_report.write(f.read() + "\n")
    print("[*] Final report generated at results/final_report.txt.")

# الدالة الرئيسية لتشغيل الأداة
def main():
    # تثبيت الأدوات المطلوبة
    install_required_tools()

    domain = input("Enter the target domain (e.g., defense.tn): ")
    
    # إنشاء مجلد لتخزين النتائج
    os.makedirs("results", exist_ok=True)

    # 1. فحص subdomains
    scan_subdomains(domain)
    
    # 2. فحص الثغرات
    scan_vulnerabilities()
    
    # 3. إنشاء تقرير شامل
    generate_report()

if __name__ == "__main__":
    main()
