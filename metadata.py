import os
import subprocess
import sys
import re
import shutil
import PyPDF2
import json
tags = set()
wordlist="rockyou.txt"
custdict="mydict"
try:
    with open(custdict,'r') as file:
        pws=[line.strip() for line in file.readlines()]
except FileNotFoundError:
    pws=[]
def get_metadata(filepath):
    try:
        output = subprocess.run(["exiftool", filepath], capture_output=True, text=True, check=True)
        print(output.stdout)
        tags = set(line.split(":")[0].strip() for line in output.stdout.splitlines())
        return tags
        try:
            out=subprocess.run(["mat2",  "--show", filepath],capture_output=True,text=True,check=True)
            print(out.stdout)
        except subprocess.CalledProcessError as e:
            print("Error running mat2 while fetching metadata:", e.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running exiftool while fetching metadata:", e.stdout)
    return set()

def remove_metadata(filepath):
    protected=False
    if ".pdf" in filepath:
        protected=check_and_correct(filepath)
    try:
        if protected:
            pw=pdfcrack(filepath,wordlist)
            #pw='dustoff'
            decrypt(filepath,pw)
        subprocess.run(["exiftool", "-overwrite_original","-all=", filepath],capture_output=True,text=True,check=True)
        if ".pdf" in filepath:
            try:
                subprocess.run(["qpdf",  "--linearize", filepath, "-",">",filepath],capture_output=True,text=True,check=True)
            except subprocess.CalledProcessError as e:
                print("Error executing QPDF linearize:", e.stdout)
        try:
            subprocess.run(["mat2",  "--inplace", "-L", filepath],capture_output=True,text=True,check=True)
        except subprocess.CalledProcessError as e:
            print("Error running MAT2 scrub:", e.stdout)
    except subprocess.CalledProcessError as e:
        #print("Error:", e.stderr)
        if "looks more like a" in e.stderr:
            match = re.search(r'([a-zA-Z]+)\s*\(looks more like a\s*([a-zA-Z]+)\)', e.stderr)
            ext1 = "." + match.group(1).lower()
            ext2 = "." + match.group(2).lower()
            new_filepath = filepath.replace(ext1, ext2)
            shutil.move(filepath, new_filepath)
            print("File extension corrected:", new_filepath)
            protected=False
            print(new_filepath)
            if ".pdf" in new_filepath:
                protected=check_and_correct(new_filepath)
            try:
                if protected:
                    pw=pdfcrack(new_filepath,wordlist)
                    decrypt(new_filepath,pw)
                subprocess.run(["exiftool",  "-overwrite_original", "-all=", new_filepath],capture_output=True,text=True,check=True)
            except subprocess.CalledProcessError as e:
                print("Error scrubbing with exiftool:", e.stdout)
            print(get_metadata(new_filepath))
            if ".pdf" in new_filepath:
                    try:
                        subprocess.run(["qpdf",  "--linearize", new_filepath, "-",">",new_filepath],capture_output=True,text=True,check=True)
                    except subprocess.CalledProcessError as e:
                        print("Error scrubbing with QPDF:", e.stdout)
            try:
                subprocess.run(["mat2",  "--inplace", "-L", new_filepath],capture_output=True,text=True,check=True)
            except subprocess.CalledProcessError as e:
                print("Error scrubbing with MAT2:", e.stdout)
            shutil.move(new_filepath, filepath)

def check_and_correct(filepath):
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfFileReader(file,strict=False)
            if pdf_reader.isEncrypted:
                print("The PDF file is encrypted.")
                return True
    except Exception as e:
        print("Error:", e)
    return False
def decrypt(filepath, password):
    try:
        subprocess.run(["qpdf","--password="+password,"--decrypt", filepath,"--replace-input"],check=True)
    except subprocess.CalledProcessError as e:
        print("Error decrypting the file.", e.stdout)

def pdfcrack(filepath, wordlist):
    try:
        if len(pws)>0:
            output=subprocess.check_output(["pdfcrack","-f",filepath,"-w",custdict]).decode("utf-8")
            lines=output.strip().split("\n")
            for line in lines:
                if "found user-password" in line:
                    crack = line.split(":")[-1].strip().strip("'")
                    print("Password cracked! It was:", crack)
                    return crack
        output=subprocess.check_output(["pdfcrack","-f",filepath,"-w",wordlist]).decode("utf-8")
        lines=output.strip().split("\n")
        for line in lines:
            if "found user-password" in line:
                crack = line.split(":")[-1].strip().strip("'")
                print("Password cracked! It was:", crack)
                if crack not in pws:
                    pws.append(crack)
                with open(custdict, 'w') as file:
                    for i in pws:
                        file.write(str(i) + '\n')
                return crack
    except subprocess.CalledProcessError as e:
        print(e.stderr)
    return None

def helper_gm(file_path):
    try:
        output = subprocess.check_output(["exiftool", "-json", file_path])
        metadata = json.loads(output)
        return metadata
    except subprocess.CalledProcessError as e:
        print("Error retrieving metadata from:",file_path,"\n", e.stdout)
        return None

def compare_metadata(file1, file2):
    print("Comparing ",file1,"and",file2)
    metadata_list1 = helper_gm(file1)
    metadata_list2 = helper_gm(file2)
    for (i, (metadata1, metadata2)) in enumerate(zip(metadata_list1, metadata_list2)):
        print(f"Comparing metadata {i + 1}:")
        # Find tags that exist in metadata2 but not in metadata1
        missing_tags = [tag for tag in metadata2.keys() if tag not in metadata1]
        if missing_tags:
            print("  Tags missing in the second metadata:")
            for tag in missing_tags:
                print(f"{tag}:{metadata2[tag]}")
 
        # Find tags that exist in both metadata1 and metadata2 but have different values
        changed_tags = [(tag, metadata1[tag], metadata2[tag]) for tag in metadata1.keys() if tag in metadata2 and metadata1[tag] != metadata2[tag]]
        if changed_tags:
            print("  Tags with changed data:")
            for tag, value1, value2 in changed_tags:
                print(f"    {tag}: {value1} -> {value2}")
    print()
    print("==========================================================================")


def magic(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            print("Currently processing:", filepath)
            tags.update(get_metadata(filepath))
            remove_metadata(filepath)
            tags.update(get_metadata(filepath))
    print("\n===Unique tags:===")
    for tag in tags:
        print(tag)

def main(action, path):
    action=action.lower()
    if action == "view":
        print(get_metadata(path))
    elif action == "scrub" or action=="clean":
        remove_metadata(path)
    elif action == "compare":
        compare_metadata(path, sys.argv[3])
    elif action == "magic" or action=="both":
        magic(path)
    elif action == "verify" or action=="test":
        test(path, sys.argv[3])
    else:
        print("Invalid action.")

def test(path1, path2):
    #uses /IMAGES and /PDF, *NOT* /allfiles
    compare_metadata(path1+"/PDF/First.pdf",path2+"/PDF/First.pdf")
    compare_metadata(path1+"/PDF/Second.pdf",path2+"/PDF/Second.pdf")
    compare_metadata(path1+"/PDF/Secrets.pdf",path2+"/PDF/Secrets.pdf")
    
    compare_metadata(path1+"/IMAGES/First.jpg",path2+"/IMAGES/First.jpg")
    compare_metadata(path1+"/IMAGES/First.png",path2+"/IMAGES/First.png")
    compare_metadata(path1+"/IMAGES/Second.jpg",path2+"/IMAGES/Second.jpg")
    compare_metadata(path1+"/IMAGES/Second.png",path2+"/IMAGES/Second.png")
    compare_metadata(path1+"/IMAGES/Secrets.jpeg",path2+"/IMAGES/Secrets.jpeg")
    compare_metadata(path1+"/IMAGES/Secrets.jpg",path2+"/IMAGES/Secrets.jpg")
    compare_metadata(path1+"/IMAGES/Secrets.png",path2+"/IMAGES/Secrets.png")
      
if __name__ == "__main__":
    if len(sys.argv) > 4:
        print("Usage: python yoinkmetadata.py <action> <path>")
    else:
        main(sys.argv[1].lower(), sys.argv[2])
    #orig/man/IMAGES and #orig/man/PDF
