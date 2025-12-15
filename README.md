Commands to run in windows from inside proj3MapReduce:
## PART 1 ##
Run code/step1_mapper.py and pipe in results/cleaned_text.txt
 - Windows command: type results\cleaned_text.txt | python code\step1_mapper.py > results\step1_map_out.txt

Sort mapper output using python:
 - Windows command: type results\step1_map_out.txt | python code\sort_mapper_output.py > results\step1_map_out_sorted.txt

Run reducer code code/step1_reducer.py with the sorted mapper output and output to topwords file
 - Windows command: type results\step1_map_out_sorted.txt | python code\step1_reducer.py > curr_step1_final.txt

## Part 2 ##
Run step 2 mapper:
 - Windows command: type results\cleaned_text.txt | python code\step2_mapper.py > results\step2_map_out.txt

Sort mapper output with python:
 - Windows command: type results\step2_map_out.txt | python code\sort_mapper_output.py > results\step2_map_out_sorted.txt

Run reducer code:
 - Windows command: type results\step2_map_out_sorted.txt | python code\step2_reducer.py > step2_analysis.txt
