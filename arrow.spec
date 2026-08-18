# Apache Arrow C++ + PyArrow. Version must stay in lock-step: pyarrow
# links the same SONAME (major*100 + minor → 25.0.x = 2500).
%define major 2500
%define libname %{mklibname arrow %{major}}
%define devname %{mklibname -d arrow}

Name:		arrow
Version:	25.0.1
Release:	1
Summary:	Columnar in-memory format and multi-language toolbox
License:	Apache-2.0
Group:		System/Libraries
URL:		https://arrow.apache.org
Source0:	https://github.com/apache/arrow/releases/download/apache-arrow-%{version}/apache-arrow-%{version}.tar.gz

# Prefer clang; LTO of Arrow + PyArrow is not worth the link RAM.
%global _lto_cflags %{nil}
# Arrow's installed CMake configs call find_dependency() on vendored
# Find*Alt modules; those generate cmake(Thrift)/cmake(BrotliAlt)/...
# requires that no OpenMandriva package Provides.
%global __requires_exclude %{?__requires_exclude:%{__requires_exclude}|}^cmake\\(

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	clang
BuildRequires:	pkgconfig(libutf8proc)
BuildRequires:	pkgconfig(re2)
BuildRequires:	pkgconfig(xsimd)
BuildRequires:	pkgconfig(snappy)
BuildRequires:	pkgconfig(liblz4)
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(libbrotlidec)
BuildRequires:	pkgconfig(libbrotlienc)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(RapidJSON)
BuildRequires:	pkgconfig(thrift)
# cmake itself Provides: cmake(Boost) with no version; the headers
# live in lib64boost-core-devel as cmake(boost_headers).
BuildRequires:	cmake(boost_headers)
# Thrift's TTransportException.h includes boost/numeric/conversion/cast.hpp
# (not part of boost_headers / lib64boost-core-devel).
BuildRequires:	boost-numeric-devel
BuildRequires:	pkgconfig(python)
BuildRequires:	python
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(wheel)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(cython)
BuildRequires:	python%{pyver}dist(numpy)
BuildRequires:	python%{pyver}dist(scikit-build-core)
BuildRequires:	python%{pyver}dist(setuptools-scm)

%description
Apache Arrow is a language-independent columnar memory format and a
set of libraries for fast data interchange. This package ships the C++
libraries (Arrow, Acero, Dataset, Parquet) used by PyArrow and by
Hugging Face datasets.

%package -n %{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries

%description -n %{libname}
Shared Arrow, Acero, Dataset and Parquet libraries.

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname}%{?_isa} = %{EVRD}
Requires:	pkgconfig(thrift)
Requires:	pkgconfig(snappy)
Requires:	pkgconfig(liblz4)
Requires:	pkgconfig(libzstd)
Requires:	pkgconfig(libbrotlidec)
Requires:	pkgconfig(re2)
Requires:	pkgconfig(libutf8proc)
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
Headers, pkg-config and CMake config for Apache Arrow C++.

%package -n python-pyarrow
Summary:	Python bindings for Apache Arrow
Group:		Development/Python
Requires:	%{libname}%{?_isa} = %{EVRD}
Requires:	python%{pyver}dist(numpy)

%description -n python-pyarrow
PyArrow, the Python API for Apache Arrow (tables, Parquet, datasets).
Required by Hugging Face datasets / TRL.

%prep
%autosetup -p1 -n apache-arrow-%{version}
# libcst is only used by a stub-docstring maintenance script, not the build.
sed -i '/libcst/d' python/pyproject.toml python/requirements-build.txt python/requirements-wheel-build.txt || true

%conf
export CC=clang
export CXX=clang++
cd cpp
# %%cmake creates cpp/build and runs cmake from there.
%cmake -G Ninja \
	-DCMAKE_C_COMPILER=clang \
	-DCMAKE_CXX_COMPILER=clang++ \
	-DARROW_DEPENDENCY_SOURCE=SYSTEM \
	-DARROW_BUILD_SHARED:BOOL=ON \
	-DARROW_BUILD_STATIC:BOOL=OFF \
	-DARROW_BUILD_TESTS:BOOL=OFF \
	-DARROW_BUILD_EXAMPLES:BOOL=OFF \
	-DARROW_BUILD_UTILITIES:BOOL=OFF \
	-DARROW_COMPUTE:BOOL=ON \
	-DARROW_CSV:BOOL=ON \
	-DARROW_JSON:BOOL=ON \
	-DARROW_FILESYSTEM:BOOL=ON \
	-DARROW_ACERO:BOOL=ON \
	-DARROW_DATASET:BOOL=ON \
	-DARROW_PARQUET:BOOL=ON \
	-DARROW_IPC:BOOL=ON \
	-DARROW_WITH_BROTLI:BOOL=ON \
	-DARROW_WITH_LZ4:BOOL=ON \
	-DARROW_WITH_SNAPPY:BOOL=ON \
	-DARROW_WITH_ZLIB:BOOL=ON \
	-DARROW_WITH_ZSTD:BOOL=ON \
	-DARROW_USE_XSIMD:BOOL=ON \
	-DARROW_SIMD_LEVEL=DEFAULT \
	-DARROW_JEMALLOC:BOOL=OFF \
	-DARROW_MIMALLOC:BOOL=OFF \
	-DARROW_FLIGHT:BOOL=OFF \
	-DARROW_GANDIVA:BOOL=OFF \
	-DARROW_ORC:BOOL=OFF \
	-DARROW_S3:BOOL=OFF \
	-DARROW_AZURE:BOOL=OFF \
	-DARROW_GCS:BOOL=OFF \
	-DARROW_CUDA:BOOL=OFF \
	-DARROW_PYTHON:BOOL=OFF \
	-DARROW_USE_CCACHE:BOOL=OFF \
	-DPARQUET_REQUIRE_ENCRYPTION:BOOL=OFF

%build
export CC=clang
export CXX=clang++
/usr/bin/ninja -C cpp/build %{?_smp_mflags}

%install
export CC=clang
export CXX=clang++
DESTDIR=%{buildroot} /usr/bin/ninja -C cpp/build install

# PyArrow against the just-installed C++ tree (not a second bundled copy).
export CMAKE_PREFIX_PATH="%{buildroot}%{_prefix}${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"
export PKG_CONFIG_PATH="%{buildroot}%{_libdir}/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
export LD_LIBRARY_PATH="%{buildroot}%{_libdir}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
export PYARROW_WITH_PARQUET=1
export PYARROW_WITH_DATASET=1
export PYARROW_WITH_ACERO=1
export PYARROW_BUNDLE_ARROW_CPP=0
export PYARROW_BUILD_TYPE=Release
export PYARROW_PARALLEL=%{_smp_build_ncpus}
export CMAKE_BUILD_PARALLEL_LEVEL=%{_smp_build_ncpus}
cd python
mkdir -p ../RPMBUILD_wheels
pip wheel --wheel-dir ../RPMBUILD_wheels --no-deps --no-build-isolation --verbose .
pip install --root=%{buildroot} --no-deps --verbose --ignore-installed \
	--no-warn-script-location --no-index --no-cache-dir \
	--find-links ../RPMBUILD_wheels ../RPMBUILD_wheels/pyarrow-*.whl

# Drop C++ static leftovers if any slipped through
rm -f %{buildroot}%{_libdir}/libarrow*.a \
	%{buildroot}%{_libdir}/libparquet*.a \
	%{buildroot}%{_libdir}/libarrow_bundled_dependencies.a 2>/dev/null || true

%files -n %{libname}
%license LICENSE.txt
%doc NOTICE.txt README.md
%{_libdir}/libarrow.so.%{major}*
%{_libdir}/libarrow_acero.so.%{major}*
%{_libdir}/libarrow_compute.so.%{major}*
%{_libdir}/libarrow_dataset.so.%{major}*
%{_libdir}/libparquet.so.%{major}*

%files -n %{devname}
%{_includedir}/arrow
%{_includedir}/parquet
%{_libdir}/libarrow.so
%{_libdir}/libarrow_acero.so
%{_libdir}/libarrow_compute.so
%{_libdir}/libarrow_dataset.so
%{_libdir}/libparquet.so
%{_libdir}/pkgconfig/arrow.pc
%{_libdir}/pkgconfig/arrow-acero.pc
%{_libdir}/pkgconfig/arrow-compute.pc
%{_libdir}/pkgconfig/arrow-csv.pc
%{_libdir}/pkgconfig/arrow-dataset.pc
%{_libdir}/pkgconfig/arrow-filesystem.pc
%{_libdir}/pkgconfig/arrow-json.pc
%{_libdir}/pkgconfig/parquet.pc
%{_libdir}/cmake/Arrow/
%{_libdir}/cmake/ArrowAcero/
%{_libdir}/cmake/ArrowCompute/
%{_libdir}/cmake/ArrowDataset/
%{_libdir}/cmake/Parquet/
%{_datadir}/arrow/
%{_datadir}/gdb/auto-load%{_libdir}/libarrow.so.*-gdb.py
%{_docdir}/arrow/

%files -n python-pyarrow
%{python_sitearch}/pyarrow
%{python_sitearch}/pyarrow-*.dist-info
