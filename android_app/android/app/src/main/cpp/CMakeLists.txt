cmake_minimum_required(VERSION 3.22.1)
project(phantom_llama)

set(CMAKE_CXX_STANDARD 17)

# Set up llama.cpp variables
set(LLAMA_BUILD_TESTS OFF CACHE BOOL "Build tests" FORCE)
set(LLAMA_BUILD_EXAMPLES OFF CACHE BOOL "Build examples" FORCE)
set(LLAMA_MMPROJ ON CACHE BOOL "Build multimodal support" FORCE)

add_subdirectory(llama.cpp)

add_library(phantom_llama SHARED phantom_jni.cpp)

target_link_libraries(phantom_llama
    llama
    log
)