def clean_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(file_path, 'w', encoding='utf-8') as file:
        for line in lines:
            if not line.startswith("Processed image:"):
                file.write(line)

if __name__ == "__main__":
    file_path = 'cleaned.txt'  # Replace with the path to your text file
    clean_file(file_path)