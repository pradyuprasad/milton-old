1. pick which category we're looking at
2. if it's GDP/inflation pick if its sector or total economy
    a. if it's total economy, return the main CSV for each (in what format??)
    b. if it is sector, pass on to sector selection (line 4)
3. If it is unemployment
    a. return whichever is the correct dataset
4. Sector specific picking
a. GDP - pick from seasonally adjusted. Match with sector, and then subsector. 
- Pick a sector 
- if we are confident about the sector
    - Level1 = Sector
    - and the sector has subsectors then:
        - pick the correct subsector
- if we are not confident about it then
    - pick subsector from all subsectors
    - if we are confident about the subsector we picked, then return only one subsector
        - else return the list of the top 3
        - 
b. Inflation - pick supersector, sector, subsector as needed
