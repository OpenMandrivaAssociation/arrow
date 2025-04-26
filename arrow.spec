%define major 2000
%define libname %mklibname arrow
%define devname %mklibname arrow -d
%define staticname %mklibname arrow -d -s

Name:		arrow
Version:	20.0.0
Release:	1
Source0:	https://github.com/apache/arrow/releases/download/apache-arrow-%{version}/apache-arrow-%{version}.tar.gz
Summary:	Columnar format and multi-language toolbox for fast data interchange and in-memory analytic
URL:		https://arrow.apache.org/
License:	Apache-2.0
Group:		System/Libraries
BuildRequires:	cmake
BuildRequires:	ninja

%description
Apache Arrow is a universal columnar format and multi-language toolbox for fast
data interchange and in-memory analytics. It contains a set of technologies
that enable data systems to efficiently store, process, and move data.

%package -n %{libname}
Summary:	Columnar format and multi-language toolbox for fast data interchange and in-memory analytic
Group:		System/Libraries

%description -n %{libname}
Apache Arrow is a universal columnar format and multi-language toolbox for fast
data interchange and in-memory analytics. It contains a set of technologies
that enable data systems to efficiently store, process, and move data.

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} = %{EVRD}

%description -n %{devname}
Development files (Headers etc.) for %{name}.

Apache Arrow is a universal columnar format and multi-language toolbox for fast
data interchange and in-memory analytics. It contains a set of technologies
that enable data systems to efficiently store, process, and move data.

%package -n %{staticname}
Summary:	Static library files for %{name}
Group:		Development/C
Requires:	%{libname} = %{EVRD}

%description -n %{staticname}
Static library files for %{name}.

Apache Arrow is a universal columnar format and multi-language toolbox for fast
data interchange and in-memory analytics. It contains a set of technologies
that enable data systems to efficiently store, process, and move data.

%prep
%autosetup -p1 -n apache-arrow-%{version}

%conf
cd cpp
%cmake -G Ninja

%build
%ninja_build -C cpp/build

%install
%ninja_install -C cpp/build

%files -n %{libname}
%{_libdir}/libarrow.so.%{major}*

%files -n %{devname}
%doc %{_docdir}/arrow
%{_includedir}/arrow
%{_libdir}/libarrow.so
%{_libdir}/pkgconfig/arrow.pc
%{_libdir}/cmake/Arrow
%{_datadir}/gdb/auto-load%{_libdir}/libarrow.so.*-gdb.py
%{_datadir}/arrow/gdb

%files -n %{staticname}
%{_libdir}/libarrow_bundled_dependencies.a
%{_libdir}/libarrow.a
