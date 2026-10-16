dd=hypot(i-1150,j-3680)-2850;
glw=exp(-(pow((i-2030)/330,2)+pow((j-870)/340,2)))*pow(max(0,min(1,(2400-i)/260)),1.5);
bse=0.13+0.36*pow(j/1080,1.9);
atmo=dd>0 ? 0.42*exp(-dd/45)+0.16*exp(-dd/240) : 0;
mdd=abs(350*(i-300)+1800*(j-440))/1833.7;
mlk=0.17*exp(-pow(mdd/190,2))*(0.3+1.1*u[1]);
rgd=hypot(i-680,j-585)-340;
rg=0.22*exp(-pow(rgd/16,2))+0.07*exp(-pow(rgd/70,2));
skyv=rg+bse+0.66*glw+atmo+mlk+0.07*(u[1]-0.5);
pr=hypot(i-680,j-585)/340;
sx=(i-680)/340; sy=(j-585)/340; sz=sqrt(max(0,1-sx*sx-sy*sy));
day=max(0,min(1,(sx*0.88+sy*0.22-sz*0.42+0.02)/0.2));
planet=rg+0.07+0.12*pow(pr,6)+0.62*pow(day,0.7)+0.06*(u[2]-0.5);
pin=max(0,min(1,(1-pr)*85+0.5));
skyv=pin*planet+(1-pin)*skyv;
cld=max(0,min(1,(u[2]-0.45)*3.2));
erth=rg+0.22+0.48*cld+0.45*exp(dd/40)+0.18*exp(dd/260)+0.45*glw-0.12*pow(j/1080,3);
mix=max(0,min(1,dd/3+0.5));
max(0,min(1,mix*skyv+(1-mix)*erth))
