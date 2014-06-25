function [pss_pos,N_id_2, freqoffset] = lte_pss_filter_sync(invec, fftl)
%filter invec with iir filter to obtain pss frequency range
%correlate with time zadoff chu sequence


cpl=144*(fftl/2048);
cpl0=160*fftl/2048;
slot_symbs=7*fftl+6*cpl+cpl0;
fs=slot_symbs/0.0005;
decim=fs/960000/2;


%filter invec and downsample
filt = FIR_Filter128FFT(fs);
disp(['lte_pss_filter_sync: filtering length:' num2str(length(invec))]);
disp(cost(filt));

tic
invec_filtered=filter(filt,invec);
invec_filtered_down=downsample(invec_filtered,decim);
toc



chu=zeros(63,3);
f_vec_fftl=zeros(fftl,3);

for i=1:3
    % Generate Zadoff_Chu sequences with DC subcarrier
    chu_seq=lte_pss_zc(i-1);
    chu(:,i)=[chu_seq(1:31);0;chu_seq(32:end)];
    
    pss=[zeros(5,1);chu(1:end,i);zeros(5,1)];
    %freq vector for big fft, fine sync
    f_vec_fftl(:,i)=[pss(37:end);zeros(fftl-length(pss),1);pss(1:36)];
end



chu_t_low=zeros(128,3);
chu_t_high=zeros(fftl,3);

%transform to time domain
for i=1:3
    chu_t_high(:,i)=ifft(f_vec_fftl(:,i), fftl);
    chu_t_high_filtered(:,i)=filter(filt,chu_t_high(:,i));
   %chu_t_low(:,i)=downsample(chu_t_high(:,i),decim);
    chu_t_low(:,i)=downsample(chu_t_high_filtered(:,i),decim);
end

chu_t_corr=chu_t_low(:,1)+chu_t_low(:,2)+chu_t_low(:,3);



%coarse sync:
disp('lte_pss_filter_sync begin coarse time sync');
n_symb=slot_symbs*10/decim;
corrmax=0;
posmax=0;
N_id_2=-1;


figure(1);

Ru=0;
corrvec=zeros(n_symb,1);

%differential correlation
for d=1:n_symb
    A0=xcorr(invec_filtered_down(d+32*0:d+32*1-1,1),chu_t_corr( 1:32) ,0);
    A1=xcorr(invec_filtered_down(d+32*1:d+32*2-1,1),chu_t_corr(33:64) ,0);
    A2=xcorr(invec_filtered_down(d+32*2:d+32*3-1,1),chu_t_corr(65:96) ,0);
    A3=xcorr(invec_filtered_down(d+32*3:d+32*4-1,1),chu_t_corr(97:128),0);
    
    Ru=A0*conj(A1)+A1*conj(A2)+A2*conj(A3);

    A0=xcorr(invec_filtered_down(d+32*0:d+32*1-1,2),chu_t_corr( 1:32) ,0);
    A1=xcorr(invec_filtered_down(d+32*1:d+32*2-1,2),chu_t_corr(33:64) ,0);
    A2=xcorr(invec_filtered_down(d+32*2:d+32*3-1,2),chu_t_corr(65:96) ,0);
    A3=xcorr(invec_filtered_down(d+32*3:d+32*4-1,2),chu_t_corr(97:128),0);
    
    Ru=Ru+A0*conj(A1)+A1*conj(A2)+A2*conj(A3);
    corrvec(d)=abs(Ru);
end
subplot(2,1,1);
hold on;
plot(abs(corrvec));
[c, p] = max(corrvec);
plot(p,c,'d');
hold off;
title('corr at low rate with filtered data, differential correlation')



% corrvec1=xcorr(invec_filtered_down(1:n_symb,1), chu_t_corr);
% corrvec1=corrvec1(n_symb+1:end);
% corrvec2=xcorr(invec_filtered_down(1:n_symb,2), chu_t_corr);
% corrvec2=corrvec2(n_symb+1:end);
% [c, p] = max(abs(corrvec1)+abs(corrvec2));
% 
% %plotting
% subplot(2,1,1);
% hold on;
% plot(abs(corrvec1)+abs(corrvec2));
% plot(p,c,'d');
% hold off;
% title('corr at low rate with filtered data');

posmax=p-1;
corrmax=0;



%calculate N_id_2
for i=1:3
    corr1=xcorr(invec_filtered_down(posmax+1:end,1), chu_t_low(:,i),0);
    corr2=xcorr(invec_filtered_down(posmax+1:end,2), chu_t_low(:,i),0);
    c= max(abs(corr1)+abs(corr2));
    
    if c > corrmax
        corrmax=abs(c);
        N_id_2=i-1;
    end
end





% disp(['coarse pos:' num2str(posmax) ' corrval:' num2str(corrmax) ' N_id_2=' num2str(N_id_2)]);
% posmax=mod(posmax,slot_symbs*10/decim);
disp(['coarse pos:' num2str(posmax)]);
disp(['Nid2:' num2str(N_id_2)]);
disp(['coarse pos modulo:' num2str(mod(posmax,slot_symbs*10/decim))]);

disp('lte_pss_filter_sync begin fine time sync');

%subtract constant filter delay
filtdelay=grpdelay(filt);
filtdelay=filtdelay(1);

finepos=decim*posmax;
clear corrvec;
clear posmax;
clear corrmax;
tic


corrvec1=xcorr(invec(finepos+1:end,1), chu_t_high(:, N_id_2+1),decim*500);
corrvec2=xcorr(invec(finepos+1:end,2), chu_t_high(:, N_id_2+1),decim*500);

[c, p] = max(abs(corrvec1)+abs(corrvec2));
finepos=finepos+p-decim-1;
corrmax=abs(c);



toc
subplot(2,1,2);
hold on;
plot(abs(corrvec1)+abs(corrvec2));
plot(p,c,'d');
hold off;
title('corr at high rate with unfiltered data');

disp(['fine pos:' num2str(finepos) ' corrval:' num2str(corrmax) ' N_id_2=' num2str(N_id_2)]);
pss_pos=finepos;




a1=xcorr(invec(finepos+1:end,1),chu_t_high(1:fftl/2, N_id_2+1),0);
a2=xcorr(invec(finepos+1+fftl/2:end,1),chu_t_high(fftl/2+1:fftl, N_id_2+1),0);
cfo=1/pi*angle(conj(a1)*a2);

a1=xcorr(invec(finepos+1:end,2),chu_t_high(1:fftl/2, N_id_2+1),0);
a2=xcorr(invec(finepos+1+fftl/2:end,2),chu_t_high(fftl/2+1:fftl, N_id_2+1),0);
cfo=-(cfo+1/pi*angle(conj(a1)*a2))/2;


disp(['CFO-pss-estimation:' num2str(cfo*15000)]);
freqoffset=cfo*15000;

end

