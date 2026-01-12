import xml.etree.ElementTree as ET
import json
import os
import glob
import sys

# 脚本会探测以下目录寻找 .uvprojx
SEARCH_DIRS = [".", "USER", "Project", "MDK-ARM"]
KEIL_INC_PATH = "D:/Program/Development/Keil_v5/ARM/ARMCC/include"

DEVICE_MAP = {
    "STM32F405": {"macro": "STM32F40_41xxx", "arch": "cortex-m4"},
    "STM32F407": {"macro": "STM32F40_41xxx", "arch": "cortex-m4"},
    "STM32F417": {"macro": "STM32F40_41xxx", "arch": "cortex-m4"},
    "STM32F429": {"macro": "STM32F429_439xx", "arch": "cortex-m4"},
    "STM32F401": {"macro": "STM32F401xx",    "arch": "cortex-m4"},
    "STM32F103ZE": {"macro": "STM32F10X_HD", "arch": "cortex-m3"},
    "STM32F103VE": {"macro": "STM32F10X_HD", "arch": "cortex-m3"},
    "STM32F103RC": {"macro": "STM32F10X_HD", "arch": "cortex-m3"},
    "STM32F103RB": {"macro": "STM32F10X_MD", "arch": "cortex-m3"},
    "STM32F103C8": {"macro": "STM32F10X_MD", "arch": "cortex-m3"},
}
# ===========================================

def generate_dot_clangd(output_dir, chip_config):
    """生成 .clangd 到指定的项目根目录"""
    clangd_content = f"""# cSpell:disable
CompileFlags:
  Add: [
    "-I", "{KEIL_INC_PATH}",
    "--target=arm-none-eabi",
    "-mcpu={chip_config['arch']}",
    "-D{chip_config['macro']}",
    "-DUSE_STDPERIPH_DRIVER",
    "-fms-extensions",
    "-fms-compatibility",
    "-fdeclspec",
    "-D__CC_ARM",
    "-D__ARMCC_VERSION=5060000",
    "-D__STATIC_INLINE=static inline",
    "-D__inline=inline",
    "-D__forceinline=inline",
    "-D__asm(x)=",           
    "-D__asm=",              
    "-Dasm=",                
    "-D__ALIGNED(x)=",
    "-D__task=",
    "-D__declspec(x)=",
    "-D__value_in_regs=",
    "-D__breakpoint(x)=",
    "-Wno-invalid-noreturn",
    "-Wno-unused-parameter",
    "-Wno-missing-declarations",
    "-Wno-implicit-function-declaration"
  ]

Index:
  Background: Build

Diagnostics:
  UnusedIncludes: None
  Suppress: [
    "ms_attributes_not_enabled",
    "unknown_typename",
    "pp_hash_error",
    "fatal_too_many_errors"
  ]
"""
    with open(os.path.join(output_dir, ".clangd"), "w", encoding='utf-8') as f:
        f.write(clangd_content)

def parse_keil_project(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    # 记录 .uvprojx 所在的绝对路径目录
    proj_file_dir = os.path.dirname(os.path.abspath(file_path))
    
    device_node = root.find(".//Device")
    device_name = device_node.text if device_node is not None else ""
    chip_config = {"macro": "STM32F40_41xxx", "arch": "cortex-m4"} # 默认 F4
    
    for key, config in DEVICE_MAP.items():
        if key in device_name:
            chip_config = config
            break

    defines = []
    def_node = root.find(".//VariousControls/Define")
    if def_node is not None and def_node.text:
        defines = [d.strip() for d in def_node.text.split(",") if d.strip()]
    
    if chip_config['macro'] not in defines: defines.append(chip_config['macro'])
    if "USE_STDPERIPH_DRIVER" not in defines: defines.append("USE_STDPERIPH_DRIVER")

    includes = []
    inc_node = root.find(".//VariousControls/IncludePath")
    if inc_node is not None and inc_node.text:
        for inc in inc_node.text.split(";"):
            # 路径拼接基于 .uvprojx 所在的目录
            abs_path = os.path.normpath(os.path.join(proj_file_dir, inc.strip()))
            includes.append(abs_path.replace("\\", "/"))

    sources = []
    for f_node in root.findall(".//File"):
        f_path = f_node.find("FilePath")
        if f_path is not None and f_node.find("FileType").text == "1":
            abs_src = os.path.normpath(os.path.join(proj_file_dir, f_path.text))
            sources.append(abs_src.replace("\\", "/"))
            
    return includes, defines, sources, chip_config

if __name__ == "__main__":
    # 1. 确定工作区根目录
    workspace_root = os.getcwd()
    
    # 2. 在工作区及其子目录中搜索 .uvprojx
    project_files = glob.glob("./**/*.uvprojx", recursive=True)
    if not project_files:
        print("[Error] No .uvprojx found in this directory or subdirectories!")
        sys.exit(1)
    
    # 优先选择搜索路径中最浅层的文件
    target_project = sorted(project_files, key=len)[0]
    print(f"[Info] Target Project: {target_project}")

    try:
        inc, defi, src, chip_config = parse_keil_project(target_project)
        
        # 3. 生成编译指令数据库
        cmds = []
        base_flags = ["arm-none-eabi-gcc", "-c", "-std=c99", f"-mcpu={chip_config['arch']}", "-mthumb"]
        base_flags += [f"-I{i}" for i in inc] + [f"-D{d}" for d in defi]
        
        for s in src:
            cmds.append({
                "directory": workspace_root.replace("\\", "/"), 
                "command": " ".join(base_flags) + " " + s, 
                "file": s
            })
        
        # 4. 始终将结果生成到当前运行脚本的根目录下
        with open(os.path.join(workspace_root, "compile_commands.json"), "w", encoding='utf-8') as f:
            json.dump(cmds, f, indent=4)
            
        generate_dot_clangd(workspace_root, chip_config)
        print(f"[Success] Project configured for {chip_config['macro']}.")
        print(f"          Output: {workspace_root}/compile_commands.json & .clangd")
        
    except Exception as e:
        print(f"[Error] {e}")