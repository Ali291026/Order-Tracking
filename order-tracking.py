import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="End-to-End Logistics & Container Tracker", layout="wide"
)

st.title("📦 End-to-End Order & Container Logistics Platform")

# --- 1. INITIALIZE SESSION STATE DATA ---
if "order_data" not in st.session_state:
  st.session_state.order_data = pd.DataFrame(
      columns=[
          "Order ID",
          "Supplier",
          "Product / Goods",
          "Quantity",
          "Order Date",
          "Order Status",
      ]
  )

if "container_data" not in st.session_state:
  st.session_state.container_data = pd.DataFrame(
      columns=[
          "Container Number",
          "Vessel Name",
          "Product Description",  # Included here
          "ETA",
          "Status",
          "Compliance Alert",
          "Linked Order ID",
      ]
  )

# --- SIDEBAR GLOBAL CONTROLS ---
st.sidebar.header("Global Controls")
if st.sidebar.button("⚠️ Clear All Data (Orders & Shipments)", type="primary"):
  st.session_state.order_data = pd.DataFrame(
      columns=[
          "Order ID",
          "Supplier",
          "Product / Goods",
          "Quantity",
          "Order Date",
          "Order Status",
      ]
  )
  st.session_state.container_data = pd.DataFrame(
      columns=[
          "Container Number",
          "Vessel Name",
          "Product Description",
          "ETA",
          "Status",
          "Compliance Alert",
          "Linked Order ID",
      ]
  )
  st.sidebar.success("All system data cleared!")
  st.rerun()

# --- MAIN APP TABS ---
tab_orders, tab_containers = st.tabs(
    ["🛒 1. Order Placement & Tracking", "🚢 2. Container Logistics & Compliance"]
)

# ==========================================
# TAB 1: ORDER PLACEMENT & TRACKING
# ==========================================
with tab_orders:
  st.subheader("🛒 Place a New Purchase Order")

  with st.form("add_order_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
      order_id = st.text_input(
          "Order ID / PO Number", placeholder="e.g., PO-2026-001"
      )
    with col2:
      supplier = st.text_input("Supplier Name", placeholder="e.g., Global Goods Co.")
    with col3:
      product = st.text_input(
          "Product Description", placeholder="e.g., Electronics"
      )

    col4, col5 = st.columns(2)
    with col4:
      quantity = st.number_input("Quantity", min_value=1, value=100)
    with col5:
      order_date = st.date_input("Order Date")

    order_status = st.selectbox(
        "Order Status",
        [
            "Order Placed",
            "In Production",
            "Ready for Dispatch",
            "Converted to Shipment",
        ],
    )

    submitted_order = st.form_submit_button("Submit Order")

    if submitted_order:
      if order_id.strip() == "":
        st.error("Please enter a valid Order ID.")
      else:
        new_order = pd.DataFrame([{
            "Order ID": order_id,
            "Supplier": supplier,
            "Product / Goods": product,
            "Quantity": quantity,
            "Order Date": str(order_date),
            "Order Status": order_status,
        }])
        st.session_state.order_data = pd.concat(
            [st.session_state.order_data, new_order], ignore_index=True
        )
        st.success(f"Order {order_id} recorded successfully!")
        st.rerun()

  st.markdown("---")
  st.subheader("📋 Active Orders Tracker")

  if st.session_state.order_data.empty:
    st.info("No active orders found.")
  else:
    st.dataframe(st.session_state.order_data, use_container_width=True)

    # Conversion & Management Section
    st.markdown("#### 🔄 Convert Order to Shipping Details")
    col_conv1, col_conv2 = st.columns(2)

    with col_conv1:
      order_list = st.session_state.order_data["Order ID"].tolist()
      selected_order = st.selectbox(
          "Select Order to Convert into Shipment:", order_list
      )

    with col_conv2:
      st.write("")
      st.write("")
      convert_button = st.button("Convert to Container Shipment ➡️")

    if convert_button:
      # Grab the product description from the selected order
      matched_order = st.session_state.order_data[
          st.session_state.order_data["Order ID"] == selected_order
      ]
      product_desc = (
          matched_order["Product / Goods"].values[0]
          if not matched_order.empty
          else "General Cargo"
      )

      # Update order status to Converted
      st.session_state.order_data.loc[
          st.session_state.order_data["Order ID"] == selected_order,
          "Order Status",
      ] = "Converted to Shipment"

      # Pre-create a container row linked to this order if it doesn't exist yet
      dummy_container_no = f"CONT-{selected_order}"
      if not (
          st.session_state.container_data["Linked Order ID"] == selected_order
      ).any():
        new_shipment = pd.DataFrame([{
            "Container Number": dummy_container_no,
            "Vessel Name": "TBD (Update Vessel)",
            "Product Description": product_desc,
            "ETA": "2026-06-01",
            "Status": "In Transit",
            "Compliance Alert": f"Converted from Order {selected_order}",
            "Linked Order ID": selected_order,
        }])
        st.session_state.container_data = pd.concat(
            [st.session_state.container_data, new_shipment], ignore_index=True
        )
        st.success(
            f"Successfully converted Order {selected_order} into Container"
            f" Shipment {dummy_container_no}! Check Tab 2."
        )
        st.rerun()
      else:
        st.warning("This order has already been converted to a shipment.")

# ==========================================
# TAB 2: CONTAINER & COMPLIANCE TRACKER
# ==========================================
with tab_containers:
  st.subheader("🚢 Container Logistics & Compliance Board")

  col_main, col_delete = st.columns([3, 1])

  with col_main:
    search_query = st.text_input(
        "🔍 Search by Container, Vessel, Product, or Linked Order:", value=""
    )
    df_containers = st.session_state.container_data

    if search_query:
      df_containers_filtered = df_containers[
          df_containers["Container Number"]
          .str.contains(search_query, case=False, na=False)
          | df_containers["Vessel Name"]
          .str.contains(search_query, case=False, na=False)
          | df_containers["Product Description"]
          .str.contains(search_query, case=False, na=False)
          | df_containers["Linked Order ID"]
          .str.contains(search_query, case=False, na=False)
      ]
    else:
      df_containers_filtered = df_containers

    if df_containers_filtered.empty:
      st.info("No container shipments found.")
    else:
      st.dataframe(df_containers_filtered, use_container_width=True)

  with col_delete:
    st.subheader("🗑️ Delete Shipment")
    if not st.session_state.container_data.empty:
      cont_list = st.session_state.container_data["Container Number"].tolist()
      selected_cont_to_delete = st.selectbox(
          "Select Container to Remove:", cont_list, key="delete_cont_select"
      )

      if st.button("Delete Selected Shipment"):
        st.session_state.container_data = st.session_state.container_data[
            st.session_state.container_data["Container Number"]
            != selected_cont_to_delete
        ].reset_index(drop=True)
        st.success(f"Removed container: {selected_cont_to_delete}")
        st.rerun()
    else:
      st.caption("No shipments available.")

  # Export Option
  st.markdown("---")
  if not st.session_state.container_data.empty:
    csv_data = st.session_state.container_data.to_csv(index=False).encode(
        "utf-8"
    )
    st.download_button(
        label="📥 Export Container Tracker to CSV",
        data=csv_data,
        file_name="container_logistics_tracker.csv",
        mime="text/csv",
    )