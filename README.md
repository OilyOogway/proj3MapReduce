Commands to run in windows from inside proj3MapReduce:

Run code/step1_mapper.py and pipe in results/cleaned_text.txt
 - Windows command: type results\cleaned_text.txt | python .\code\step1_mapper.py > results/step1_map_out.txt

Run reducer code code/step1_reducer.py with the sorted mapper output and output to topwords file
 - Windows command: type results\step1_map_out_1.txt | Sort-Object | python code\step1_reducer.py > curr_step1_final.txt

