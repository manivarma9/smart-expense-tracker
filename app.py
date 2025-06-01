import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

# ---------------------- DATABASE SETUP ----------------------
conn = sqlite3.connect("expenses.db", check_same_thread=False)
c = conn.cursor()

# Add date column if not exists
c.execute(''' 
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount INTEGER NOT NULL,
        date TEXT NOT NULL
    )
''')
conn.commit()

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="Smart Expense Tracker", layout="centered")
st.title("💸 Smart Expense Tracker Dashboard")
st.markdown("Track your expenses and visualize them in charts 📊")

# ---------------------- INPUT FORM ----------------------
with st.form("add_form"):
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        category = st.text_input("📝 Category", placeholder="e.g. Food, Travel, Rent")
    with col2:
        amount = st.number_input("💵 Amount", min_value=1)
    with col3:
        exp_date = st.date_input("📅 Date", value=date.today())
    add_btn = st.form_submit_button("➕ Add Expense")
    if add_btn:
        if not category.strip():
            st.warning("⚠️ Category cannot be empty!")
        elif amount <= 0:
            st.warning("⚠️ Amount must be greater than zero!")
        else:
            c.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)", 
                      (category.strip(), amount, exp_date.isoformat()))
            conn.commit()
            st.success(f"✅ Added {category} - ₹{amount} on {exp_date}")
            st.experimental_rerun()

# ---------------------- FETCH DATA ----------------------
df = pd.read_sql("SELECT * FROM expenses", conn)
if not df.empty:
    df['date'] = pd.to_datetime(df['date'])

# ---------------------- FILTERS ----------------------
st.subheader("🔍 Filter Expenses")

filter_col1, filter_col2, filter_col3 = st.columns([3, 3, 4])
with filter_col1:
    categories = ["All"] + sorted(df['category'].unique().tolist()) if not df.empty else ["All"]
    selected_cat = st.selectbox("Category", categories)
with filter_col2:
    start_date = st.date_input("Start Date", value=df['date'].min() if not df.empty else date.today())
with filter_col3:
    end_date = st.date_input("End Date", value=df['date'].max() if not df.empty else date.today())

filtered_df = df.copy()
if selected_cat != "All":
    filtered_df = filtered_df[filtered_df['category'] == selected_cat]
filtered_df = filtered_df[(filtered_df['date'] >= pd.to_datetime(start_date)) & 
                          (filtered_df['date'] <= pd.to_datetime(end_date))]

# ---------------------- TOTAL EXPENSE DISPLAY ----------------------
total_expense = filtered_df['amount'].sum() if not filtered_df.empty else 0
st.markdown(f"### Total Expenses: ₹{total_expense}")

# ---------------------- DISPLAY TABLE ----------------------
st.subheader("📋 Expense Table")
if not filtered_df.empty:
    st.dataframe(filtered_df[['id', 'category', 'amount', 'date']], use_container_width=True)
else:
    st.info("No expenses to show for selected filters.")

# ---------------------- DELETE OPTION ----------------------
st.subheader("❌ Delete an Expense")
if not filtered_df.empty:
    delete_id = st.selectbox("Select ID to Delete", filtered_df['id'])
    if st.button("Delete"):
        c.execute("DELETE FROM expenses WHERE id = ?", (delete_id,))
        conn.commit()
        st.success(f"Deleted Expense ID {delete_id}")
        st.experimental_rerun()

# ---------------------- EDIT EXPENSE FEATURE ----------------------
st.subheader("✏️ Edit an Expense")
if not filtered_df.empty:
    edit_id = st.selectbox("Select ID to Edit", filtered_df['id'])
    selected_expense = filtered_df[filtered_df['id'] == edit_id].iloc[0]
    
    new_category = st.text_input("Edit Category", value=selected_expense['category'])
    new_amount = st.number_input("Edit Amount", min_value=1, value=int(selected_expense['amount']))
    new_date = st.date_input("Edit Date", value=selected_expense['date'])
    
    if st.button("Update Expense"):
        if not new_category.strip():
            st.warning("⚠️ Category cannot be empty!")
        elif new_amount <= 0:
            st.warning("⚠️ Amount must be greater than zero!")
        else:
            c.execute("UPDATE expenses SET category = ?, amount = ?, date = ? WHERE id = ?",
                      (new_category.strip(), new_amount, new_date.isoformat(), edit_id))
            conn.commit()
            st.success(f"Updated Expense ID {edit_id}")
            st.experimental_rerun()

# ---------------------- CHART VISUALIZATION ----------------------
st.subheader("📈 Visualize Expenses")

if not filtered_df.empty:
    chart_type = st.selectbox("Choose Chart Type", ["Pie Chart", "Bar Chart", "Line Chart"])

    grouped = filtered_df.groupby('category')['amount'].sum()

    if chart_type == "Pie Chart":
        fig1, ax1 = plt.subplots()
        ax1.pie(grouped, labels=grouped.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax1.axis('equal')
        st.pyplot(fig1)

    elif chart_type == "Bar Chart":
        st.bar_chart(grouped)

    elif chart_type == "Line Chart":
        # For line chart, let's plot amount over time by category
        time_grouped = filtered_df.groupby(['date', 'category'])['amount'].sum().unstack(fill_value=0)
        st.line_chart(time_grouped)

else:
    st.info("Add some expenses to see charts.")
