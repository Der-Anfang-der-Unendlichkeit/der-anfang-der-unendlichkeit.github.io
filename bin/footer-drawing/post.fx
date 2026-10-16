dd=hypot(i-1150,j-3680)-2850;
fa=u[4]; tth=u[5];
skya=max(0,min(1,dd/3+0.5))*(1-fa);
er=max(max(u[1]*skya,u[2]*skya),u[3]*skya);
er=max(er,max(u[7],u[8])*(1-fa));
er=er*(0.78+0.22*tth);
pp=u[0]+(1-u[0])*er;
pp=pp*(1-0.8*u[9]);
topy=10+60*u[6].p{i,500};
fd=max(0,min(1,(j-topy)/140)); fd=fd*fd*(3-2*fd);
1-(1-pp)*fd
