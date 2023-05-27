import logging

import openai
import json


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



# fake api key for public sharing
openai.api_key = "wh-SB03IT99DWWWbCCC5C13TBlbkFJMcoPGHG9HxoOupAuUwkkstw"

examples = {
    "Mark's birthday is on the 31st": {
        "subject": "Alex",
        "event": "Birthday",
        "date": "!31",
        "enumerated": "BIRTHDAY",
        "more_info": ""
    },
    "Joanne wants to go skiing in 5 days": {
        "subject": "Joanne",
        "event": "Ski Trip",
        "date": "+5",
        "enumerated": "EVENT",
        "more_info": ""
    },
    "TODO: Check Shufersal refund for 200 shekels in 2 days": {
        "subject": "Shufersal",
        "event": "Refund",
        "date": "+2",
        "enumerated": "OTHER",
        "more_info": "200 shekels"
    },
    "The salary should arrive on the 10th": {
        "subject": "Me",
        "event": "Salary",
        "date": "!10",
        "enumerated": "MONTHLY_REMINDER",
        "more_info": ""
    },
    "Cibus renews on the 23rd of every month": {
        "subject": "Cibus",
        "event": "Renewal",
        "date": "!23",
        "enumerated": "MONTHLY_REMINDER",
        "more_info": ""
    },
    "Ann's birthday is on the 26th of September": {
        "subject": "Ann",
        "event": "Birthday",
        "date": "09-26",
        "enumerated": "BIRTHDAY",
        "more_info": ""
    },
    "Reminder: Check up on kids tomorrow": {
        "subject": "Kids",
        "event": "Check Up",
        "date": "+1",
        "enumerated": "OTHER",
        "more_info": ""
    },
    "I should plan Sarah's birthday party, which is next week": {
        "subject": "Sarah",
        "event": "Birthday Party Planning",
        "date": "+7",
        "enumerated": "OTHER",
        "more_info": ""
    },
    "Rent is due next week": {
        "subject": "Me",
        "event": "Payment",
        "date": "+7",
        "enumerated": "MONTHLY_REMINDER",
        "more_info": ""
    },
    "My father's birthday is Jan 10, he wanted a pony": {
        "subject": "My Father",
        "event": "Birthday",
        "date": "01-10",
        "enumerated": "BIRTHDAY",
        "more_info": "He wants a pony"
    },
    "Developers Institute deadline for hackathon is May 28th": {
        "subject": "Developers Institute",
        "event": "Hackathon Deadline",
        "date": "05-28",
        "enumerated": "OTHER",
        "more_info": ""
    }
}


def parse_user_input_single_attempt(user_input: str):
    completion_help = '{"subject": "'  # This helps ChatGPT give good a JSON output

    # We trick ChatGPT into believing it already gave us some answers
    message_history = [{"role": "system",
                        "content": "Enumerated field should be one of the following: BIRTHDAY, ANNIVERSARY, "
                                   "MONTHLY_REMINDER, EVENT, OTHER."}]

    # Add examples to chat history
    for k, v in examples.items():
        message_history.append({"role": "user", "content": k})
        message_history.append({"role": "assistant", "content": json.dumps(v)})

    # Add user query
    message_history.append({"role": "user", "content": user_input})

    # A bit more help...
    message_history.append({"role": "assistant", "content": completion_help})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.75,
        max_tokens=256,
        messages=message_history
    )

    # output = {"subject": " + whatever ChatGPT gives us, hopefully a valid JSON
    output = completion_help + completion.choices[0].message.content

    logging.info(output)

    # in case ChatGPT adds some text after the valid JSON.
    try:
        output, _ = output.rsplit("}", maxsplit=1)
        output = output + "}"
    except:
        return None

    try:
        valid_dict = json.loads(output)
        if "date" in valid_dict.keys() and "subject" in valid_dict.keys() and "event" in valid_dict.keys():
            return valid_dict
        else:
            print("Some keys are missing, check gpt prompt to fix this...")
            for k, v in valid_dict.items():
                print(k, v)
            return None
    except:
        # Invalid JSON
        return None


def parse_user_input(text: str, max_attempts=10):
    for attempt in range(max_attempts):
        response = parse_user_input_single_attempt(text)
        if response is not None: return response

    # We've reached the end of the loop, seems ChatGPT doesn't want to give us a good output :(
    return None
