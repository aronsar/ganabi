# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.14

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/local/Cellar/cmake/3.14.5/bin/cmake

# The command to remove a file.
RM = /usr/local/Cellar/cmake/3.14.5/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env

# Include any dependencies generated for this target.
include CMakeFiles/pyhanabi.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/pyhanabi.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/pyhanabi.dir/flags.make

CMakeFiles/pyhanabi.dir/pyhanabi.cc.o: CMakeFiles/pyhanabi.dir/flags.make
CMakeFiles/pyhanabi.dir/pyhanabi.cc.o: pyhanabi.cc
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/pyhanabi.dir/pyhanabi.cc.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/pyhanabi.dir/pyhanabi.cc.o -c /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env/pyhanabi.cc

CMakeFiles/pyhanabi.dir/pyhanabi.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/pyhanabi.dir/pyhanabi.cc.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env/pyhanabi.cc > CMakeFiles/pyhanabi.dir/pyhanabi.cc.i

CMakeFiles/pyhanabi.dir/pyhanabi.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/pyhanabi.dir/pyhanabi.cc.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env/pyhanabi.cc -o CMakeFiles/pyhanabi.dir/pyhanabi.cc.s

# Object files for target pyhanabi
pyhanabi_OBJECTS = \
"CMakeFiles/pyhanabi.dir/pyhanabi.cc.o"

# External object files for target pyhanabi
pyhanabi_EXTERNAL_OBJECTS =

libpyhanabi.dylib: CMakeFiles/pyhanabi.dir/pyhanabi.cc.o
libpyhanabi.dylib: CMakeFiles/pyhanabi.dir/build.make
libpyhanabi.dylib: hanabi_lib/libhanabi.a
libpyhanabi.dylib: CMakeFiles/pyhanabi.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX shared library libpyhanabi.dylib"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/pyhanabi.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/pyhanabi.dir/build: libpyhanabi.dylib

.PHONY : CMakeFiles/pyhanabi.dir/build

CMakeFiles/pyhanabi.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/pyhanabi.dir/cmake_clean.cmake
.PHONY : CMakeFiles/pyhanabi.dir/clean

CMakeFiles/pyhanabi.dir/depend:
	cd /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env /Users/admin/Desktop/Research/Hanabi/ganabi/hanabi_env/CMakeFiles/pyhanabi.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/pyhanabi.dir/depend
