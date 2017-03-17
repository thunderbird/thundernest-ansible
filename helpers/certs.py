import executor
import os

def get():
    python3env = os.environ.copy()
    python3dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/letsencrypt/bin:'

    python3env['PATH'] = python3dir + python3env['PATH']

    commands = [
            ["~/dehydrated/dehydrated --register --accept-terms"],
            ["~/dehydrated/dehydrated -c -t dns-01 -k '../dehydrated/hooks/cloudflare/hook.py'"],
    ]

    executor.run(commands, env=python3env, shell=True)


def main():
    get()

if __name__ == '__main__':
    main()
