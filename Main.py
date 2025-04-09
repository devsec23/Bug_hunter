import os
import subprocess

# الأدوات المطلوبة
tools = {
    "subfinder": "subfinder",
    "amass": "amass",
    "sqlmap": "sqlmap/sqlmap.py",
    "nikto": "nikto",
    "arachni": "arachni"
}

# إنشاء مجلدات النتائج
os.makedirs("results/sqlmap", exist_ok=True)
os.makedirs("results/nikto", exist_ok=True)
os.makedirs("results/arachni", exist_ok=True)

# التحقق من تثبيت الأدوات أو محاولة تثبيتها
for tool, path in tools.items():
    if os.path.exists(path) or subprocess.call(f"which {tool}", shell=True, stdout=subprocess.DEVNULL) == 0:
        print(f"[+] {tool} is already installed.")
    else:
        print(f"[!] {tool} not found, installing...")
        if tool == "sqlmap":
            os.system("git clone https://github.com/sqlmapproject/sqlmap.git")
        elif tool == "arachni":
            print("[!] Arachni requires manual install or Docker. Skipping...")
        else:
            os.system(f"apt install -y {tool}")

# إدخال الموقع
target = input("Enter the target domain (e.g., example.com): ").strip()
print(f"[*] Scanning subdomains for {target}")

# تشغيل subfinder و amass
os.system(f"subfinder -d {target} -o results/subfinder.txt")
os.system(f"amass enum -d {target} -o results/amass.txt")

# دمج النتائج + إضافة الدومين الرئيسي
all_domains = set()
for path in ["results/subfinder.txt", "results/amass.txt"]:
    with open(path) as f:
        all_domains.update(line.strip() for line in f if line.strip())

all_domains.add(target)

with open("results/merged_domains.txt", "w") as f:
    for domain in sorted(all_domains):
        f.write(domain + "\n")

print(f"[*] Total discovered domains (including main domain): {len(all_domains)}")

# الفحص لكل نطاق
for domain in all_domains:
    print(f"[*] Scanning {domain} for vulnerabilities...")
    url = f"http://{domain}"

    sqlmap_out = f"results/sqlmap/{domain}.txt"
    os.system(f"python3 sqlmap/sqlmap.py -u {url} --batch --output-dir=results/sqlmap/{domain} > {sqlmap_out} 2>&1")

    arachni_out = f"results/arachni/{domain}.txt"
    os.system(f"echo '[!] Skipping arachni scan for {domain} (cloud shell limitation)' > {arachni_out}")

    nikto_out = f"results/nikto/{domain}.txt"
    os.system(f"nikto -h {url} -o {nikto_out}")

print("[*] All scans finished. Check results folder.")
