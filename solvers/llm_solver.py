import os
from typing import List

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


class SudokuResponse(BaseModel):
    solution: List[List[int]] = Field(
        description="Grid of sized N x N representing the solved Sudoku."
    )


def solve(grid):
    n = len(grid)

    parser = PydanticOutputParser(pydantic_object=SudokuResponse)
    model = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash", temperature=0
    )

    prompt_text = (
        "You are an expert Sudoku solver. "
        "Given a partially filled N x N Sudoku grid, fill in the missing numbers according to Sudoku rules. "
        "Return only the completed grid in the specified format.\n\n"
        "{format_instructions}\n"
        "Tablero:\n{grid}"
    )

    prompt = ChatPromptTemplate.from_template(prompt_text)

    chain = prompt | model | parser

    try:
        ans = chain.invoke(
            {
                "n": n,
                "grid": grid,
                "format_instructions": parser.get_format_instructions(),
            }
        )

        sol_ia = ans.solution

        if len(sol_ia) == n and all(len(row) == n for row in sol_ia):
            for i in range(n):
                for j in range(n):
                    grid[i][j] = sol_ia[i][j]
            return grid
        else:
            # print("Incorrect solution format received from LLM.")
            return None

    except Exception:
        # print(f"LLM Error: {e}")
        return None
