from sender import Sender
import argparse


description_string = 'Send a message to Firebase Cloud Messaging servers.'


def parseOptions():
    """
    Return a tuple containing the topic and the message given in the command
    line options.
    """
    parser = argparse.ArgumentParser(description=description_string)
    parser.add_argument("-t",
                        help="Topic to send the message (default is global).")
    parser.add_argument("message", help="The message to send.")
    args = parser.parse_args()
    return (args.t if args.t else "global", args.message)


def main():
    (topic, message) = parseOptions()
    sender = Sender()
    sender.send_message(message, topic)

if __name__ == "__main__":
    main()
