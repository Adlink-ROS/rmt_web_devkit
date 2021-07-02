# minimum cmake version
cmake_minimum_required(VERSION 3.10)

# project name, version
project(server_example VERSION 1.0.0)

# Build server_example.c
add_executable(server_example server_example.c)

# Link RMT library
target_link_libraries(server_example PRIVATE rmt_server_shared)
