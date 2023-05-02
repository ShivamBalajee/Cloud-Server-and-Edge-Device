import csv
import tempfile

def get_precautions():
    with open('formatted_symptoms.csv', newline='') as csv_tempfile:
        # Create a temporary file for writing
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpfile:
            # Write the CSV data to the temporary file
            writer = csv.writer(tmpfile)
            reader = csv.reader(csv_tempfile)
            for row in reader:
                writer.writerow(row)

            # Get the name of the temporary file
            tmpfilename = tmpfile.name

    with open(tmpfilename, 'r') as input_file:
        csv_reader = csv.reader(input_file)
        
        # Read the first row of the file
        header_row = next(csv_reader)
        
        # Count the number of columns
        num_columns = len(header_row)

    # Print the number of columns
    for i in range(num_columns-1): 
        column_values = {}
        counter = 1
        for column_index_to_extract in range(1, num_columns):
            with open(tmpfilename, newline='') as csvfile:
                reader = csv.reader(csvfile)

                # Get the number of rows in the CSV file
                rows = list(reader)
                num_rows = len(rows)
                if num_rows == 1:
                    break

            with open(tmpfilename, 'r') as input_file:
                csv_reader = csv.reader(input_file)
                header_row = next(csv_reader)
                column_name = header_row[column_index_to_extract]
                
                # Iterate over each row in the file
                for row in csv_reader:
            
                    # Extract the value of the desired column and append it to the list
                    column_value = row[column_index_to_extract]
                    if column_value not in column_values.values():
                        column_values[counter] = column_value
                        counter += 1
        print('--Symptoms--')
        for key,value in column_values.items():
            print(f"{key} .   {value}")
        user_symptom = input("Enter the symptom from the following")
        print(column_values[int(user_symptom)])

        with open(tmpfilename, 'r') as input_file:
            reader = csv.reader(input_file)
            headers = next(reader)
            data = [row for row in reader]

        # set up initial filter and sorting criteria
        filter_value = column_values[int(user_symptom)]

        filtered_data = [row for row in data if row[1] == filter_value or row[2] == filter_value or row[3] == filter_value]

        # Write the filtered data to a new CSV file
        with open(tmpfilename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # Write the header row
            writer.writerows(filtered_data)

    with open(tmpfilename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            disease = row[0]
            print(disease)
    with open('symptom_precaution.csv', 'r') as input_file:
            reader = csv.reader(input_file)
            headers = next(reader)
            data = [row for row in reader]

            filtered_data = [row for row in data if row[0] == disease]
    
    # print('These are the precautions to be followed: ')
    # print(f' 1. {filtered_data[0][1]}')
    # print(f' 2. {filtered_data[0][2]}')
    # print(f' 3. {filtered_data[0][3]}')
    return {'precautions':filtered_data[0]}