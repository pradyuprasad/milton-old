from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,field_validator 
from ..agent_code.models import SelectDatasetOutput
from ..agent_code.external_dataset_selector import select_dataset
from ..agent_code.main_agent import AI_agent, sector_selected_already, compare_between_fixed_sectors, compare_all_sectors, do_anything, whole_economy
from ..agent_code.models import SelectDataPointsOutput
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal, List


gdp_sectors = {
    "Manufacturing", "Construction", "Utilities", "Other Goods Industries",
    "Wholesale & Retail Trade", "Transportation & Storage", "Accommodation & Food Services",
    "Information & Communications", "Finance & Insurance",
    "Real Estate, Professional Services And Administrative & Support Services",
    "Other Services Industries"
}

inflation_sectors = {
    "Food", "Food Excl Food Serving Services", "Food Serving Services",
    "Clothing & Footwear", "Housing & Utilities", "Household Durables & Services",
    "Health Care", "Transport", "Communication", "Recreation & Culture", 
    "Education", "Miscellaneous Goods & Services",
    "Bread & Cereals", "Meat", "Fish & Seafood", "Milk, Cheese & Eggs", "Oils & Fats",
    "Fruits", "Vegetables", "Sugar, Preserves & Confectionery", "Non-Alcoholic Beverages",
    "Other Food", "Restaurant Food", "Fast Food", "Hawker Food", "Catered Food",
    "Clothing", "Other Articles & Related Services", "Footwear", "Accommodation",
    "Utilities & Other Fuels", "Household Durables", "Household Services & Supplies",
    "Medicines & Health Products", "Outpatient Services", "Hospital Services", "Health Insurance",
    "Private Transport", "Public Transport", "Other Transport Services", "Postage & Courier Services",
    "Telecommunication Equipment", "Telecommunication Services", "Recreational & Cultural Goods",
    "Recreational & Cultural Services", "Newspapers, Books & Stationery", "Holiday Expenses",
    "Tuition & Other Fees", "Textbooks & Study Guides", "Personal Care", "Alcoholic Drinks & Tobacco",
    "Personal Effects", "Social Services", "Other Miscellaneous Services"
}

class SelectDataPointsInput(BaseModel):
    sector: str
    type: Literal['unemployment', 'inflation', 'GDP']
    query: str = None 

class CompareSectorsInput(BaseModel):
    sectors: List[str]
    type: Literal['inflation', 'GDP']
    query: str = None 

class CompareAllSectors(BaseModel):
    type: Literal['inflation', 'GDP']
    query: str = None

class WholeEconomy(BaseModel):
    type: Literal['inflation', 'GDP', 'unemployment']
    query: str = None


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class QueryInput(BaseModel):
    query: str


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/select-dataset-external")
async def external_dataset_selector(input: QueryInput):
    print("got data")
    query = input.query
    output: SelectDatasetOutput = select_dataset(query=query)
    return output.model_dump()


@app.post("/select-datapoints")
async def select_datapoints(input: QueryInput):
    query = input.query
    try:
        answer:SelectDataPointsOutput = AI_agent(query)
        print(answer.model_dump())
        return answer.model_dump()
    except Exception as e:
        print(str(e))
        answer: SelectDataPointsOutput = SelectDataPointsOutput(working=False, answer="An error happened")

@app.post("/select-datapoints-sector")
async def select_datapoints_fixed_sector(input: SelectDataPointsInput):
    print(f"Received input: {input}")
    print(f"Input sector: {input.sector}")
    print(f"Input type: {input.type}")
    print(f"Valid sectors for {input.type}: {inflation_sectors if input.type == 'inflation' else gdp_sectors}")
    
    # Manual validation check
    if input.type == 'inflation' and input.sector not in inflation_sectors:
        raise HTTPException(status_code=400, detail=f"Invalid sector '{input.sector}' for type 'inflation'.")
    elif input.type in ['unemployment', 'GDP'] and input.sector not in gdp_sectors:
        raise HTTPException(status_code=400, detail=f"Invalid sector '{input.sector}' for type '{input.type}'.")

    try:
        result = sector_selected_already(input.sector, input.type, input.query)
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/compare-between-specific-sectors")
async def compare_specific_sectors(input: CompareSectorsInput):
    print(f"Received input: {input}")
    print(f"Input sector: {input.sectors}")
    print(f"Input type: {input.type}")
    print(f"Valid sectors for {input.type}: {inflation_sectors if input.type == 'inflation' else gdp_sectors}")

    if input.type == 'inflation':
        for sector in input.sectors:
            if sector not in inflation_sectors:
                raise HTTPException(status_code=400, detail=f"Invalid sector '{sector}' for type 'inflation'.")
    elif input.type == 'GDP':
        for sector in input.sectors:
            if sector not in gdp_sectors:
                raise HTTPException(status_code=400, detail=f"Invalid sector '{sector}' for type 'GDP'.")
    
    try:
        return compare_between_fixed_sectors(sectors=input.sectors, type_of=input.type, query=input.query)
    
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Something went wrong internally! {str(e)}")
        




@app.post("/compare-all-sectors")
async def compare_all_sectors_endpoint(input: CompareAllSectors):
    try:
        result = compare_all_sectors(input.type, input.query)
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ask-anything")
async def ask_anything(input:QueryInput):
    try:
        ans = do_anything(input.query)
        return ans
    except Exception as e:
        print(e)
        return SelectDataPointsOutput(working=False, answer='')

@app.post("/whole-economy")
async def whole_economy_endpoint(input: WholeEconomy):
    try:
        ans = whole_economy(input.type, query=input.query)
        return ans
    except Exception as e:
        print(e)
        return SelectDataPointsOutput(working=False, answer='')