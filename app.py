import streamlit as st
from PIL import Image
from google import genai
import json
import re
import time
from io import BytesIO

# ==========================================
# NUTRISMART AI - CONNECTED APPLICATION
# ==========================================

st.set_page_config(
    page_title="NutriSmart AI",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 NutriSmart AI")
st.subheader("Eat Healthy, Spend Smart!")

st.write(
    "Upload your own food image to explore nutrition, "
    "healthier alternatives, and affordable meal ideas."
)

# ==========================================
# API CONNECTION
# ==========================================

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    api_ready = True

except Exception:
    api_ready = False
    client = None

if not api_ready:
    st.error(
        "Gemini API key not found. Please check "
        ".streamlit/secrets.toml."
    )
    st.stop()


# ==========================================
# STEP 1: UPLOAD ANY IMAGE OR TAKE A PHOTO
# ==========================================

st.divider()
st.header("📸 Upload Your Image")

st.write(
    "Upload any image you want. AI will try to determine "
    "whether it contains food."
)

image_option = st.radio(
    "Choose an option:",
    ["Upload Image", "Take Photo"],
    horizontal=True
)

uploaded_image = None

if image_option == "Upload Image":

    uploaded_file = st.file_uploader(
        "Choose an image from your device",
        type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded_file is not None:
        try:
            uploaded_image = Image.open(
                BytesIO(uploaded_file.getvalue())
            ).convert("RGB")

        except Exception:
            st.error("This image could not be opened.")

else:
    camera_file = st.camera_input("Take a photo")

    if camera_file is not None:
        try:
            uploaded_image = Image.open(
                BytesIO(camera_file.getvalue())
            ).convert("RGB")

        except Exception:
            st.error("This camera image could not be opened.")


# ==========================================
# STEP 2: AI FOOD RECOGNITION
# ==========================================

if uploaded_image is not None:

    st.image(
        uploaded_image,
        caption="Your uploaded image",
        use_container_width=True
    )

    # Store image bytes to detect when a new image is uploaded.
    image_bytes = BytesIO()
    uploaded_image.save(image_bytes, format="JPEG")
    current_image = image_bytes.getvalue()

    if st.session_state.get("current_image") != current_image:
        st.session_state["current_image"] = current_image
        st.session_state.pop("food_analysis", None)
if st.button("🤖 Analyse My Image", type="primary"):

    if uploaded_image is None:
        st.warning("Please upload a food image first.")

    else:
        prompt = """
        Examine the provided image carefully.

        Determine whether the image contains food or a drink.

        Return ONLY a valid JSON object with these keys:
        {
          "is_food": true,
          "food_name": "name of food or drink",
          "confidence": "high, medium, or low",
          "description": "brief description",
          "nutrition_per_100g": {
            "calories": 100,
            "protein": 2.0,
            "carbs": 15.0,
            "fat": 3.0
          },
          "healthier_alternatives": [
            "alternative 1",
            "alternative 2",
            "alternative 3"
          ],
          "nutrition_note": "brief explanation"
        }

        Instructions:
        - Accept unfamiliar and international foods.
        - Do not assume every image contains food.
        - For non-food images, set is_food to false.
        - Do not invent food names.
        - Nutrition values must be approximate estimates.
        - Estimate nutrition per 100 grams.
        - Use low confidence when uncertain.
        - Return valid JSON only.
        """

        try:
            with st.spinner(
                "AI is analysing your image. Please wait..."
            ):
                response = None

                for attempt in range(3):
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[
                                prompt,
                                uploaded_image
                            ]
                        )
                        break

                    except Exception as api_error:
                        error_message = str(api_error)

                        if "503" in error_message and attempt < 2:
                            wait_time = 5 * (2 ** attempt)

                            st.warning(
                                f"Gemini is busy. "
                                f"Retrying in {wait_time} seconds..."
                            )

                            time.sleep(wait_time)
                        else:
                            raise

                if response is None:
                    raise RuntimeError(
                        "Gemini did not return a response."
                    )

                response_text = response.text or ""

                response_text = re.sub(
                    r"^```(?:json)?\s*|\s*```$",
                    "",
                    response_text.strip(),
                    flags=re.IGNORECASE
                )

                result = json.loads(response_text)

                st.session_state["food_analysis"] = result

            st.success("Food analysis completed!")

        except Exception as e:
            st.error("Image analysis failed.")
            st.caption(f"Technical details: {e}")


    if uploaded_image is None:
        st.warning("Please upload a food image first.")

    else:
        prompt = """
        Examine the provided image carefully.

        Determine whether the image contains food or a drink.

        Return ONLY a valid JSON object with these keys:
        {
          "is_food": true,
          "food_name": "name of food or drink",
          "confidence": "high, medium, or low",
          "description": "brief description",
          "nutrition_per_100g": {
            "calories": 100,
            "protein": 2.0,
            "carbs": 15.0,
            "fat": 3.0
          },
          "healthier_alternatives": [
            "alternative 1",
            "alternative 2",
            "alternative 3"
          ],
          "nutrition_note": "brief explanation"
        }

        Instructions:
        - Accept unfamiliar and international foods.
        - Do not assume every image contains food.
        - For non-food images, set is_food to false.
        - Do not invent food names.
        - Nutrition values must be approximate estimates.
        - Estimate nutrition per 100 grams.
        - Use low confidence when uncertain.
        - Return valid JSON only.
        """

        try:
            with st.spinner(
                "AI is analysing your image. Please wait..."
            ):
                response = None

                for attempt in range(3):
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[
                                prompt,
                                uploaded_image
                            ]
                        )
                        break

                    except Exception as api_error:
                        error_message = str(api_error)

                        if "503" in error_message and attempt < 2:
                            wait_time = 5 * (2 ** attempt)

                            st.warning(
                                f"Gemini is busy. "
                                f"Retrying in {wait_time} seconds..."
                            )

                            time.sleep(wait_time)
                        else:
                            raise

                if response is None:
                    raise RuntimeError(
                        "Gemini did not return a response."
                    )

                response_text = response.text or ""

                response_text = re.sub(
                    r"^```(?:json)?\s*|\s*```$",
                    "",
                    response_text.strip(),
                    flags=re.IGNORECASE
                )

                result = json.loads(response_text)

                st.session_state["food_analysis"] = result

            st.success("Food analysis completed!")

        except Exception as e:
            st.error("Image analysis failed.")
            st.caption(f"Technical details: {e}")

    
# STEP 3: CONNECTED NUTRITION ANALYSIS
# =======================================
    analysis = st.session_state.get("food_analysis")

if analysis is not None:

    st.divider()
    st.header("🔎 AI Recognition Result")
    if not isinstance(analysis, dict):
        st.error("Invalid AI response. Please upload the image again.")

    elif not analysis.get("is_food", False):
        st.warning(
            "The image was not identified as food. "
            "Please upload a clear food image and try again."
        )
    else:
        st.success("Food identified successfully!")
        st.write("### Food Details")
        for key, value in analysis.items(): st.write(f"**{key.replace('_', ' ').title()}:** {value}")

        # Food details
        st.subheader(f"🍽️ Food Name: {analysis.get('food_name', 'Unknown')}")
        st.write("**Confidence:**", analysis.get("confidence", "Unknown"))
        st.write("**Description:**", analysis.get("description", "Not available"))

        # Nutrition information
        nutrition = analysis.get("nutrition_per_100g", {})

        st.subheader("🥗 Nutrition per 100 g")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Calories", f"{nutrition.get('calories', 0)} kcal")

        with col2:
            st.metric("Protein", f"{nutrition.get('protein', 0)} g")

        with col3:
            st.metric("Carbohydrates", f"{nutrition.get('carbs', 0)} g")

        with col4:
            st.metric("Fat", f"{nutrition.get('fat', 0)} g")

        # Healthier alternatives
        st.subheader("💚 Healthier Alternatives")

        alternatives = analysis.get("healthier_alternatives", [])

        if alternatives:
            for food in alternatives:
                st.write(f"✅ {food}")
        else:
            st.info("No alternatives available.")

        # Nutrition note
        note = analysis.get("nutrition_note", "")

        if note:
            st.info(f"💡 Nutrition Tip: {note}")


    
        # ==========================================
        # STEP 4: HEALTHIER ALTERNATIVES
        # ==========================================
        food_name=analysis.get("food_name","Unknown food")
        st.divider()
        st.header("💚 Healthier Twin Food Finder")

        alternatives = analysis.get(
            "healthier_alternatives",
            []
        )

        if alternatives:

            st.write(
                f"Possible alternatives to **{food_name}**:"
            )

            for alternative in alternatives:
                st.write(f"🌱 {alternative}")

        else:
            st.info(
                "No suitable alternatives were returned "
                "for this image."
            )

        st.caption(
            "Alternatives are general suggestions. The "
            "healthier choice depends on ingredients, "
            "preparation, portion size, and individual needs."
        )


        # ==========================================
        # STEP 5: BUDGET MEAL OPTIMIZER
        # ==========================================

        st.divider()
        st.header("💰 Budget Meal Optimizer")

        st.write(
            "Plan an affordable meal using your budget "
            "and food preference."
        )

        budget = st.number_input(
            "Your meal budget (₹):",
            min_value=10,
            max_value=10000,
            value=100,
            step=10,
            key="connected_meal_budget"
        )

        preference = st.selectbox(
            "Food preference:",
            [
                "Vegetarian",
                "Vegetarian + Eggs",
                "Non-vegetarian"
            ],
            key="connected_food_preference"
        )

        # Illustrative prices and nutrition per serving.
        meal_foods = {
            "Rice": {
                "cost": 8,
                "protein": 2.7,
                "calories": 130,
                "diet": "Vegetarian"
            },
            "Dal": {
                "cost": 15,
                "protein": 9.0,
                "calories": 116,
                "diet": "Vegetarian"
            },
            "Banana": {
                "cost": 6,
                "protein": 1.3,
                "calories": 105,
                "diet": "Vegetarian"
            },
            "Milk": {
                "cost": 12,
                "protein": 6.6,
                "calories": 122,
                "diet": "Vegetarian"
            },
            "Chapati": {
                "cost": 5,
                "protein": 3.0,
                "calories": 100,
                "diet": "Vegetarian"
            },
            "Egg": {
                "cost": 8,
                "protein": 6.3,
                "calories": 72,
                "diet": "Egg"
            },
            "Chicken": {
                "cost": 35,
                "protein": 27.0,
                "calories": 165,
                "diet": "Non-vegetarian"
            }
        }

        if preference == "Vegetarian":
            available_foods = {
                name: details
                for name, details in meal_foods.items()
                if details["diet"] == "Vegetarian"
            }

        elif preference == "Vegetarian + Eggs":
            available_foods = {
                name: details
                for name, details in meal_foods.items()
                if details["diet"] in [
                    "Vegetarian",
                    "Egg"
                ]
            }

        else:
            available_foods = meal_foods.copy()

        st.write(
            f"Your uploaded food was identified as "
            f"**{food_name}**. Choose foods below to "
            "build a budget-friendly meal."
        )

        selected_foods = st.multiselect(
            "Choose foods for your meal:",
            options=list(available_foods.keys()),
            default=[],
            key="connected_selected_foods"
        )

        if st.button(
            "Calculate My Meal Budget",
            key="connected_calculate_budget"
        ):

            if not selected_foods:

                st.warning(
                    "Please select at least one food."
                )

            else:

                total_cost = sum(
                    available_foods[name]["cost"]
                    for name in selected_foods
                )

                total_protein = sum(
                    available_foods[name]["protein"]
                    for name in selected_foods
                )

                total_calories = sum(
                    available_foods[name]["calories"]
                    for name in selected_foods
                )

                st.subheader("Your Meal Summary")

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Estimated Cost",
                    f"₹{total_cost}"
                )

                c2.metric(
                    "Protein",
                    f"{total_protein:.1f} g"
                )

                c3.metric(
                    "Calories",
                    f"{total_calories:.0f} kcal"
                )

                if total_cost <= budget:
                    st.success(
                        f"Your selected meal is within "
                        f"your ₹{budget} budget!"
                    )

                else:
                    st.warning(
                        f"Your selected meal exceeds "
                        f"your budget by "
                        f"₹{total_cost - budget}."
                    )

                st.write("### Selected foods")

                for name in selected_foods:
                    st.write(
                        f"- {name}: "
                        f"₹{available_foods[name]['cost']}"
                    )

        st.caption(
            "Meal prices and nutrition values are illustrative "
            "estimates. This version calculates the cost of "
            "foods you select; it does not automatically find "
            "the cheapest or nutritionally optimal meal."
        )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "NutriSmart AI | AI Image Analysis | Nutrition "
    "Estimates | Healthier Alternatives | Budget Meal Planning"
)
