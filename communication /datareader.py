import time
import multiprocessing

# Function to simulate reading data
def data_reader(output_queue):
    for i in range(5):
        time.sleep(1)  # Simulate time taken to read data
        data = f"data_{i}"
        print(f"Data Reader: Read {data}")
        output_queue.put(data)  # Send data to next process
    
    # Once data reading is done, signal the processor to stop
    output_queue.put("END")  # Use "END" to indicate the end of data

if __name__ == "__main__":
    # Create a queue for inter-process communication
    queue = multiprocessing.Queue()

    # Start the data_reader process
    reader_process = multiprocessing.Process(target=data_reader, args=(queue,))
    reader_process.start()

    # Wait for the reader to finish
    reader_process.join()

    print("Data Reader has finished.")
