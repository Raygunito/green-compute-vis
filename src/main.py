import kagglehub

path = kagglehub.dataset_download("ashyou09/global-data-center-and-ai-waterelectricity-usage", output_dir="data")
print("Path to dataset files:", path)