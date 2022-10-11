# pynest/CMakeLists.txt
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

find_package(Cython)

message( STATUS "We are going to check HAVE_PYTHON: ${HAVE_PYTHON}" )

if ( HAVE_PYTHON )

  message( STATUS "We are going to check CYTHON_FOUND: ${CYTHON_FOUND}" )
  if ( CYTHON_FOUND )

      message( STATUS "Adding targets!" )
      add_cython_target ( pynestkernel pynestkernel.pyx CXX PY3)
      add_cython_target ( nestkernel_api nestkernel_api.pyx CXX PY3)

      add_library(pynestkernel MODULE ${pynestkernel})
      set_target_properties(pynestkernel PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}")
      add_library(nestkernel_api MODULE ${nestkernel_api})
      set_target_properties(nestkernel_api PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}")
  else ()
    message( FATAL_ERROR "You have configured NEST to build the Python bindings PyNEST, but "
          "there is no Cython version found on your system." )
  endif ()

  target_link_libraries( pynestkernel
      nest_lib nestutil nestkernel sli_lib
      ${SLI_MODULES} ${EXTERNAL_MODULE_LIBRARIES}
      )

  target_link_libraries( nestkernel_api
      nest_lib nestutil nestkernel sli_lib
      ${SLI_MODULES} ${EXTERNAL_MODULE_LIBRARIES}
      )

  target_include_directories( pynestkernel PRIVATE
      ${PROJECT_BINARY_DIR}/libnestutil
      ${PROJECT_SOURCE_DIR}/libnestutil
      ${PROJECT_SOURCE_DIR}/pynest
      ${PROJECT_SOURCE_DIR}/nestkernel
      ${PROJECT_SOURCE_DIR}/nestkernel/spatial
      ${PROJECT_SOURCE_DIR}/sli
      ${PROJECT_SOURCE_DIR}/thirdparty
      ${SLI_MODULE_INCLUDE_DIRS}
      ${Python_INCLUDE_DIRS}
      )
  target_include_directories( nestkernel_api PRIVATE
      ${PROJECT_BINARY_DIR}/libnestutil
      ${PROJECT_SOURCE_DIR}/libnestutil
      ${PROJECT_SOURCE_DIR}/pynest
      ${PROJECT_SOURCE_DIR}/nestkernel
      ${PROJECT_SOURCE_DIR}/nestkernel/spatial
      ${PROJECT_SOURCE_DIR}/sli
      ${PROJECT_SOURCE_DIR}/thirdparty
      ${SLI_MODULE_INCLUDE_DIRS}
      ${Python_INCLUDE_DIRS}
      )

  target_compile_definitions( pynestkernel PRIVATE
      -D_IS_PYNEST
      )
  target_compile_definitions( nestkernel_api PRIVATE
      -D_IS_PYNEST
      )

  install(DIRECTORY  nest/ ${PROJECT_BINARY_DIR}/pynest/nest/
      DESTINATION ${CMAKE_INSTALL_PREFIX}/${PYEXECDIR}/nest
      PATTERN "versionchecker.py.in" EXCLUDE
  )
  install( TARGETS pynestkernel DESTINATION ${PYEXECDIR}/nest/ )
  install( TARGETS nestkernel_api DESTINATION ${PYEXECDIR}/nest/ )

  install( DIRECTORY examples/
      DESTINATION ${CMAKE_INSTALL_DOCDIR}/examples/pynest
  )

endif ()
