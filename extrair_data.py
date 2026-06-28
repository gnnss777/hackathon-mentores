from pathlib import Path
import json

orig = Path("C:/OPENCODE/HACKATON/index.html").read_text(encoding="utf-8")

start = orig.find("var DATA=")
end = orig.find("\n\nvar N =", start)
data_str = orig[start:end].strip().rstrip(";")

data_str_clean = data_str.replace("var DATA=", "")
data = json.loads(data_str_clean)
print(f"DATA: {len(data)} mentores")

bios_start = orig.find("var BIOS = {")
bios_end = orig.find("\n};", bios_start) + 3
bios_str = orig[bios_start:bios_end].strip().rstrip(";")
bios_str_clean = bios_str.replace("var BIOS = ", "")
bios = json.loads(bios_str_clean)
print(f"BIOS: {len(bios)} entradas")

Path("C:/OPENCODE/HACKATON/mentores_data.json").write_text(
    json.dumps({"data": data, "bios": bios}, ensure_ascii=False),
    encoding="utf-8"
)
print("Salvo em mentores_data.json")
