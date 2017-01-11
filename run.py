import sys, os, subprocess

def main():
    if len(sys.argv) == 2:
      DBName = sys.argv[1]
      input_path = "data/"+DBName+"/input.in"
      output_log_path = "data/"+DBName+"/output.log"
      output_path = "public_html/output/"+DBName
      #------------------------------------------------------------------------
      try:
        runnable = ["downloader.py","classifier.py","cleaning.py","modelling.py","diagnostics.py","report.py"]
        for afile in runnable:
            command = "python " + afile + " " + input_path + " > " + output_log_path
            retcode = subprocess.check_call(command, stderr=subprocess.STDOUT, shell=True)
        os.chdir(output_path)
        command = "pandoc "+DBName+".tex -s --latexmathml -o "+DBName+".html"
        retcode = subprocess.check_call(command, stderr=subprocess.STDOUT, shell=True)
        command = "pdflatex "+DBName+".tex"
        retcode = subprocess.check_call(command, stderr=subprocess.STDOUT, shell=True)
        command = "pdflatex "+DBName+".tex"
        retcode = subprocess.check_call(command, stderr=subprocess.STDOUT, shell=True)
        print("Successful !!!", retcode)
      except Exception as e:
        print("Execution failed:", e)
      #------------------------------------------------------------------------
    else:
        print("Error! arguments less or more than 1")
main()
