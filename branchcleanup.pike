#!/usr/local/bin/pike
int main()
{
	foreach (Process.run(({"git","branch"}))->stdout/"\n",string l)
		if (sizeof(l)>2 && l[2..]!="master")
			Process.create_process(({"git","branch","-d",l[2..]}))->wait();
}