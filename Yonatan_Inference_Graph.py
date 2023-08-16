import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import itertools

# Load your data
data = pd.read_csv("../GWU_result.csv")  # Replace with the actual path to your data

st.markdown("# Yonatan model Analysis")


total_hate = data[data["Label"] == "Hate"].shape[0]
total_non_hate = data[data["Label"] == "Non Hate"].shape[0]
selected_rows = data[data["n_flavors"] > 1]
total_multiple_targets = len(selected_rows)

# Display the total counts using Markdown formatting
st.markdown(f"**Total Hate:** {total_hate}")
st.markdown(f"**Total Non-Hate:** {total_non_hate}")
st.markdown(f"**Total Multiple Targets:** {total_multiple_targets}")

# Grouped tag vs hate/non-hate bar graph (Graph 1)
grouped_data = data.groupby(["GroupedTAGS", "Label"]).size().reset_index(name="Count")
fig1 = px.bar(grouped_data, x="GroupedTAGS", y="Count", color="Label", barmode="group", title="Categories vs Hate/Non-Hate", text_auto=True)
st.plotly_chart(fig1)


# List of targets and TAGS
targets = ["Religion_PRED", "Race_PRED", "Gender_PRED", "Gender Identity/Sexual Orientation_PRED", "Immigration_PRED", "Ethnicity/Identitarian/Nationalism_PRED", "Anti-semitism_PRED"]
tags = ["Mainstream News", "Social Justice", "LGBT", "White Identitarian", "AntiSJW"]

tag_target_data = []
for tag in tags:
    tag_subset = data[data["GroupedTAGS"] == tag]
    total_hate_count = tag_subset[tag_subset["Label"] == "Hate"].shape[0]
    target_hate_count = {target: 0 for target in targets}
    multiple_targets_count = 0
    for index, row in tag_subset.iterrows():
        n_flavors = row["n_flavors"]
        if n_flavors > 1:
            multiple_targets_count += 1
        else:
            for target in targets:
                target_hate_count[target] += row[target]
    target_hate_count["Multiple Targets"] = multiple_targets_count
    for target, count in target_hate_count.items():
        if target == "Multiple Targets":
            target_name = target
        else:
            target_name = target.replace("_PRED", "").replace("Identity/Sexual Orientation_PRED", "Identity/Sex Orientation_PRED")
        tag_target_data.append({"Tag": tag, "Target": target_name, "Count": count,
                                "Total": total_hate_count})
tag_target_df = pd.DataFrame(tag_target_data)

# Create the horizontal bar chart
fig2 = px.bar(tag_target_df,  y="Count", x="Tag", color="Target", custom_data=["Total"],
             orientation="v",
             title="Categories vs Targets Count")

# Customize the hover template
fig2.update_traces(hovertemplate="Tag: %{x}<br>Target: %{fullData.name}<br>Total Hate Count: %{customdata[0]}<br>Target HateCount:%{y} <extra></extra>")
st.plotly_chart(fig2)





active_columns_count = selected_rows["Active_Columns"].value_counts().reset_index()
active_columns_count.columns = ["Active_Columns", "Count"]

active_columns_count["Active_Columns"] = active_columns_count["Active_Columns"].str.replace("_PRED", "")
top_10_active_columns = active_columns_count.nlargest(10, "Count")
reversed_top_10_active_columns = top_10_active_columns.iloc[::-1]

# fig = px.bar(active_columns_count, x="Active_Columns", y="Count", title="Total Co-occureces")
# st.plotly_chart(fig)

fig3 = px.bar(reversed_top_10_active_columns, y="Active_Columns", x="Count", title="Top 10 co-occurences of multiple targets",
             orientation="h", text_auto=True)  # Set the orientation to horizontal
fig3.update_yaxes(tickfont=dict(size=9))
st.plotly_chart(fig3)




# List of targets
targets = ["Religion_PRED", "Race_PRED", "Gender_PRED", "Gender Identity/Sexual Orientation_PRED", "Immigration_PRED", "Ethnicity/Identitarian/Nationalism_PRED", "Anti-semitism_PRED"]

# Create a co-occurrence matrix
co_occurrence_matrix = pd.DataFrame(index=targets, columns=targets, data=0)

# Populate the co-occurrence matrix
for row_idx, row in data.iterrows():
    n_flavors = row["n_flavors"]
    if n_flavors > 1:
        for i, target1 in enumerate(targets):
            for j, target2 in enumerate(targets):
                if i != j:
                    co_occurrence_matrix.at[target1, target2] += row[target1] + row[target2]

# Create a bubble chart
bubble_data = []
for target1 in targets:
    for target2 in targets:
        if target1 != target2:
            bubble_data.append({"Target1": target1, "Target2": target2, "Co-occurrence": co_occurrence_matrix.loc[target1, target2]})

bubble_df = pd.DataFrame(bubble_data)
fig4 = px.scatter(
    bubble_df,
    x="Target1",
    y="Target2",
    size="Co-occurrence",
    color="Co-occurrence",
    title="Co-occurrence Density Chart"
)

st.plotly_chart(fig4)

