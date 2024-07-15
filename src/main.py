import argparse
import yaml
import watcher
import asyncio

def parse():
    # Create the parser
    parser = argparse.ArgumentParser(description="Start the ROSBridge-logger")
    
    parser.add_argument('config',  type=str,  nargs='?', default='logger.yaml', help="Patch to config file for the logger (default: logger.yaml)")

    # Parse the arguments
    return parser.parse_args()

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def log_callback(data):
    print(data)

def main():
    args = parse()
    config = read_config(args.config)
    
    log = config.get('log')

    w = watcher.RosbridgeWatcher(config.get('rosbridge'))

    topics = config.get('topics')
    runners = []
    for key, value in topics.items():
        runners.append(asyncio.gather(w.watch_topic(key, value, log_callback)))
        print(f"topic: {key}    msg: {value}")
    
    asyncio.get_event_loop().run_until_complete(*runners)



if __name__ == "__main__":
    main()
