clear

set more off
capture log close
capture graph drop _all

cd "~/Dropbox/Documents/Research/LFPR/Forecasting"

log using "logs/lfpr_by_age_sex_and_cohort_$time_string.log", append

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

drop if lfp == .
keep if inrange(age, 16, 90)
egen lfp_tot = total(lfp * (year < 2000)), by(age sex)
egen lfp_count = total((year < 2000)), by(age sex)
gen lfp_age_avg = lfp_tot / lfp_count
drop lfp_tot lfp_count

export delimited "data/lfpr_age_sex_cohort.csv", delim(",") replace nolabel
	
