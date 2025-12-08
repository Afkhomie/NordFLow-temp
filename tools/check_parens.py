from pathlib import Path
p=Path(r'C:\Users\Prakash\OneDrive\Desktop\NodeFlow\virtual_devices_setup.bat')
s=p.read_text(encoding='utf-8')
bal=0
for i,line in enumerate(s.splitlines(),start=1):
    for ch in line:
        if ch=='(':
            bal+=1
        elif ch==')':
            bal-=1
    print(f"{i:03d}: bal={bal:3d} | {line}")
print('FINAL BALANCE',bal)
