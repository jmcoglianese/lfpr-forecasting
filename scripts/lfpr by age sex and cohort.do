clear

set more off
capture log close
capture graph drop _all

cd "~/Dropbox/Documents/Research/LFPR/Forecasting"

log using "logs/lfpr_by_age_sex_and_cohort_$time_string.log", append

*-------------------------------------------------------------------------------
* Load unemployment rate from FRED for later
*-------------------------------------------------------------------------------

freduse UNRATE, clear

gen time = mofd(daten)
gen year = yofd(daten)
format time %tm
tsset time

tsdetrend_cea unrate_trend = UNRATE, window(120)

gen ugap = UNRATE - unrate_trend

collapse (mean) ugap, by(year)

tsset year
gen ugap_lag1 = L.ugap
gen ugap_lag2 = L2.ugap

save "data/ugap.dta", replace

*-------------------------------------------------------------------------------
* Load the data
*-------------------------------------------------------------------------------

!7za e "data/totpop_lfpr_panel_5.dta.gz" -o"data/"
use year age sex empstat wtfinl using "data/cps_00030.dta", clear
!rm "data/cps_00030.dta"

gen lfp = (inlist(empstat,10,12,20,21,22)) if !inlist(empstat,0,1)
gen n = 1

*-------------------------------------------------------------------------------
* Collapse and plot
*-------------------------------------------------------------------------------

collapse (mean) lfp (rawsum) n wtfinl [iw = wtfinl], by(age sex year)

replace lfp = lfp * 100
gen cohort = year - age

save "data/lfpr_age_sex_cohort.dta", replace

merge m:1 year using "data/ugap.dta", keep(1 3) assert(2 3) nogen

drop if lfp == .
keep if inrange(age, 16, 90)
egen lfp_tot = total(lfp * (year < 2000)), by(age sex)
egen lfp_count = total((year < 2000)), by(age sex)
gen lfp_age_avg = lfp_tot / lfp_count
drop lfp_tot lfp_count

export delimited "data/lfpr_age_sex_cohort.csv", delim(",") replace nolabel
	
