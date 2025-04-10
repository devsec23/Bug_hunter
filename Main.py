import os
import subprocess

# استبدال الأدوات
tools = {
    'subfinder': 'subfinder',
    'amass': 'amass',
    'sqlmap': 'sqlmap',
    'nikto': 'nikto',
    'wapiti': 'wapiti'
}

# دالة لتثبيت الأدوات إن لم تكن مثبتة
def install_tool(tool_name):
    if tool_name == "subfinder":
        os.system("go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest")
    elif tool_name == "amass":
        os.system("go install github.com/owasp/amass/v3/cmd/amass@latest")
    elif tool_name == "sqlmap":
        os.system("git clone https://github.com/sqlmapproject/sqlmap.git && cd sqlmap && python3 setup.py install")
    elif tool_name == "nikto":
        os.system("sudo apt install nikto")
    elif tool_name == "wapiti":
        os.system("sudo apt install wapiti")

# دالة لفحص الأداة إن كانت مثبتة
def check_tool_installed(tool_name):
    result = subprocess.run(['which', tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode().strip()

# فحص الأدوات وتثبيتها إن كانت غير مثبتة
for tool_name in tools.values():
    if not check_tool_installed(tool_name):
        print(f"Tool {tool_name} not found, installing...")
        install_tool(tool_name)
    else:
        print(f"Tool {tool_name} is already installed.")

# استعلام الموقع
target_domain = input("Enter the target domain (e.g., defense.tn): ")

# دالة لتنفيذ أدوات الفحص
def run_tool(tool_name, command, output_file):
    print(f"[*] Running {tool_name}...")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with open(output_file, 'wb') as f:
        f.write(result.stdout)
    print(f"[*] Results saved to {output_file}")

# فحص السب دومينات باستخدام subfinder
subdomains_file = "results/subfinder.txt"
run_tool("subfinder", ['subfinder', '-d', target_domain, '-o', subdomains_file], subdomains_file)

# فحص السب دومينات باستخدام amass
amass_file = "results/amass.txt"
run_tool("amass", ['amass', 'enum', '-d', target_domain, '-o', amass_file], amass_file)

# فحص الثغرات باستخدام sqlmap (باستخدام الرابط الأساسي)
sqlmap_file = "results/sqlmap.txt"
run_tool("sqlmap", ['sqlmap', '-u', f"http://{target_domain}", '--batch', '--output-dir=results/sqlmap'], sqlmap_file)

# فحص الثغرات باستخدام nikto
nikto_file = "results/nikto.txt"
run_tool("nikto", ['nikto', '-h', f"http://{target_domain}", '-o', nikto_file], nikto_file)

# فحص الثغرات باستخدام Wapiti
wapiti_file = "results/wapiti.txt"
run_tool("wapiti", ['wapiti', f"http://{target_domain}", '-o', wapiti_file], wapiti_file)

# دمج جميع النتائج في تقرير نهائي
final_report = "results/final_report.txt"
with open(final_report, 'w') as report:
    with open(subdomains_file, 'r') as f:
        report.write(f"[*] Subdomains from Subfinder:\n")
        report.write(f.read())
    report.write("\n\n")
    with open(amass_file, 'r') as f:
        report.write(f"[*] Subdomains from Amass:\n")
        report.write(f.read())
    report.write("\n\n")
    with open(sqlmap_file, 'r') as f:
        report.write(f"[*] SQLMap Results:\n")
        report.write(f.read())
    report.write("\n\n")
    with open(nikto_file, 'r') as f:
        report.write(f"[*] Nikto Results:\n")
        report.write(f.read())
    report.write("\n\n")
    with open(wapiti_file, 'r') as f:
        report.write(f"[*] Wapiti Results:\n")
        report.write(f.read())

print(f"[*] Final report generated at {final_report}")
