var
	a: char;
	bcd, ef: integer;
	b: real;
	c: boolean;

begin
    c := true;
    b := 1.55;
	a := 'z';
	bcd := 345;
	ef := ord(a) + bcd;

	writeln('Result: ', ef);
end.
