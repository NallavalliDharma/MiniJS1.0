from environment import Environment

# Create the global environment
global_env = Environment()

global_env.define("x", 10)

print("Global x:", global_env.get("x"))

# Create a nested environment
local_env = Environment(enclosing=global_env)

local_env.define("x", 20)

print("Local x:", local_env.get("x"))

# Update the local variable
local_env.assign("x", 30)

print("Updated local x:", local_env.get("x"))
print("Global x after assignment:", global_env.get("x"))

# Test an undefined variable
try:
    global_env.get("unknown")
except RuntimeError as error:
    print("Error:", error)
