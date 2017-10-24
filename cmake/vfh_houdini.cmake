#
# Copyright (c) 2015-2017, Chaos Software Ltd
#
# V-Ray For Houdini
#
# ACCESSIBLE SOURCE CODE WITHOUT DISTRIBUTION OF MODIFICATION LICENSE
#
# Full license text: https://github.com/ChaosGroup/vray-for-houdini/blob/master/LICENSE
#

include(CheckIncludeFile)

set(HOUDINI_VERSION       "16.0" CACHE STRING "Houdini major version")
set(HOUDINI_VERSION_BUILD "600"  CACHE STRING "Houdini build version")
set(HOUDINI_QT_VERSION    "5"    CACHE STRING "Houdini Qt version")
set(HOUDINI_INSTALL_ROOT  ""     CACHE PATH   "Houdini install path")

# Houdini 15.x is Qt 4 only.
if (HOUDINI_VERSION VERSION_LESS 16.0)
	set(HOUDINI_QT_VERSION 4 CACHE STRING "HDK < 16.x is only Qt 4.x" FORCE)
endif()

if(${HOUDINI_QT_VERSION} VERSION_LESS 5)
	set(WITH_SOHO OFF)
endif()

# Compiler version.
set(HDK_RUNTIME vc11 CACHE STRING "Houdini runtime" FORCE)
if (HOUDINI_VERSION VERSION_GREATER_EQUAL 15.5)
	set(HDK_RUNTIME vc14 CACHE STRING "Houdini runtime" FORCE)
endif()

# Made using: cat sesitag.txt | sesitag -m
set(PLUGIN_TAGINFO "\"3262197cbf104d152da5089a671b9ff8394bdcd9d530d8aa27f5984e1714bfd251aa2487851869344346dba5159b681c2da1a710878dac641a5874f82bead6fb0cb006e8bedd1ad3f169d85849f95eb181\"")

set(VFH_DSO_DIRPATH ${CMAKE_BINARY_DIR}/dso)
set(VFH_BIN_DIRPATH ${CMAKE_BINARY_DIR}/bin)
set(VFH_PYTHON_DIRPATH ${CMAKE_BINARY_DIR}/python)

find_package(HDK ${HOUDINI_VERSION}.${HOUDINI_VERSION_BUILD} REQUIRED)

set(HDK_DSO_DEFINITIONS
	-DVERSION=${HOUDINI_VERSION}
	-DHOUDINI_DSO_VERSION=${HOUDINI_VERSION}
	-DUT_DSO_TAGINFO=${PLUGIN_TAGINFO}
)

macro(use_houdini_sdk)
	message(STATUS "Using Houdini ${HOUDINI_VERSION}.${HOUDINI_VERSION_BUILD}: ${HOUDINI_INSTALL_ROOT}")
	message_array("Using HDK include path" HDK_INCLUDES)
	message_array("Using HDK library path" HDK_LIBRARIES)
	message(STATUS "HDK Qt version: ${HOUDINI_QT_VERSION}")
	if(WIN32)
		message(STATUS "HDK runtime: ${HDK_RUNTIME}")
	endif()

	# Set bin and home path
	if(APPLE)
		#TODO : need to check those
		set(HOUDINI_BIN_PATH "${HOUDINI_INSTALL_ROOT}/Houdini FX.app/Contents/MacOS")
		set(HOUDINI_HOME_PATH "$ENV{HOME}/Library/Preferences/houdini/${HOUDINI_VERSION}")
		set(HOUDINI_FRAMEWORK_ROOT "/Library/Frameworks/Houdini.framework/Versions/${HOUDINI_VERSION}.${HOUDINI_VERSION_BUILD}")

	elseif(WIN32)
		set(USER_HOME "$ENV{HOME}")
		if(USER_HOME STREQUAL "")
			set(USER_HOME "$ENV{USERPROFILE}/Documents")
		endif()
		file(TO_CMAKE_PATH "${USER_HOME}" USER_HOME)

		set(HOUDINI_BIN_PATH  "${HOUDINI_INSTALL_ROOT}/bin")
		set(HOUDINI_HOME_PATH "${USER_HOME}/houdini${HOUDINI_VERSION}")

	else()
		set(HOUDINI_BIN_PATH "${HOUDINI_INSTALL_ROOT}/bin")
		set(HOUDINI_HOME_PATH "$ENV{HOME}/houdini${HOUDINI_VERSION}")
	endif()

	add_definitions(
		${HDK_DEFINITIONS}
		${HDK_DSO_DEFINITIONS}
	)
	include_directories(${HDK_INCLUDES})
	link_directories(${HDK_LIBRARIES})
endmacro()

macro(houdini_library name sources)
	add_library(${name} STATIC ${sources})
endmacro()

macro(houdini_plugin name sources)
	add_library(${name} SHARED ${sources})
	set_target_properties(${name} PROPERTIES PREFIX "")
	target_link_libraries(${name} ${HDK_LIBS})
	vfh_osx_flags(${name})
endmacro()
