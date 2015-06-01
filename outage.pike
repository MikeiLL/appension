#!/usr/bin/env pike

constant NOTIFYEMAIL="mike@mzoo.org";
constant SMSEMAIL="2016794168@pm.sprint.com";
constant SENDEREMAIL="mikekilmer@infiniteglitch.net";
constant SERVER="http://infiniteglitch.net/";
constant PAUSE=60;
constant FAILED=0;
constant TIMEOUT=10;

int lastfailed=0;

//Send notification emails. Currently uses /usr/bin/mail in case there's some significance to it; could switch to direct SMTP (eg Protocols.SMTP.Client).
void mail(string subj,string body,int|void include_log)
{
	Process.run(({"/usr/bin/mail","-s",subj,SENDEREMAIL,SMSEMAIL}),(["stdin":body]));
	if (include_log) body+="\n"+((Stdio.read_file("debug.log")||"")/"\n")[<100..]*"\n"+"\n"; //Add the last hundred-ish lines of log
	Process.run(({"/usr/bin/mail","-s",subj,SENDEREMAIL,NOTIFYEMAIL}),(["stdin":body]));
}

void request_fail(object q)
{
	remove_call_out(request_fail);
	werror("DOWN "+ctime(time()));
	Process.create_process(({"sudo","systemctl","restart","glitch.service"}))->wait();
	if (!lastfailed) mail(SERVER+" went down",SERVER+" went down "+ctime(time()),1);
	lastfailed=0;
}

void request_ok(object q)
{
	if (q->status!=200) {request_fail(q); return;}
	werror("Up   "+ctime(time()));
	remove_call_out(request_fail);
	q->close();
	if (lastfailed) mail(SERVER+" is up again",SERVER+" is up again - "+ctime(time()));
	lastfailed=0;
}

void check()
{
	Protocols.HTTP.do_async_method("GET",SERVER,0,0,
		Protocols.HTTP.Query()->set_callbacks(request_ok,request_fail));
	call_out(request_fail,TIMEOUT);
	call_out(check,PAUSE);
}

int main() {call_out(check,0); return -1;}
