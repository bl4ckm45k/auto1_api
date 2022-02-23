from environs import Env

env = Env()
env.read_env()

login = env.str('login')
password = env.str('password')