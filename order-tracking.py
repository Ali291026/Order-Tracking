import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="End-to-End Logistics & Compliance Tracker", layout="wide"
)

st.title("📦 End-to-End Order & Container Logistics & Compliance Platform")

# --- 1. INITIALIZE SESSION STATE DATA ---
if "order_data" not in st.session_state:
  st.session_state.order_data = pd.DataFrame(
      columns=[
          "Order ID",
          "Supplier",
          "Product Description",
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
          "Product Description",
          "Quantity",
          "Bill of Lading (B/L)",
          "ACD Status",
          "COO Status",
          "SOB Date",
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
          "Product Description",
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
          "Quantity",
          "Bill of Lading (B/L)",
          "ACD Status",
          "COO Status",
          "SOB Date",
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
    ["🛒 1. Multi-Item Order Management", "🚢 2. Container Shipping & Compliance"]
)

# ==========================================
# TAB 1: ORDER MANAGEMENT (MULTI-ITEM)
# ==========================================
with tab_orders:
  st.subheader("🛒 Add Multi-Item Purchase Order")
  st.caption(
      "You can add multiple product line items under the same Order ID."
  )

  with st.form("add_order_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
      order_id = st.text_input(
          "Order ID / PO Number", placeholder="e.g., PO-2026-001"
      )
    with col2:
      supplier = st.text_input("Supplier Name", placeholder="e.g., Global Goods Co.")
    with col3:
      order_date = st.date_input("Order Date")

    st.markdown("##### Add Line Items for this Order")
    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
      product = st.text_input(
          "Product Description",
          placeholder="e.g., Steel Brackets, Model A",
          key="form_product",
      )
    with col_p2:
      quantity = st.number_input(
          "Quantity", min_value=1, value=100, key="form_qty"
      )

    order_status = st.selectbox(
        "Order Status",
        [
            "Order Placed",
            "In Production",
            "Ready for Dispatch",
            "Converted to Shipment",
        ],
    )

    submitted_order = st.form_submit_button("Add Line Item / Order")

    if submitted_order:
      if order_id.strip() == "" or product.strip() == "":
        st.error("Please enter a valid Order ID and Product Description.")
      else:
        new_order = pd.DataFrame([{
            "Order ID": order_id,
            "Supplier": supplier,
            "Product Description": product,
            "Quantity": quantity,
            "Order Date": str(order_date),
            "Order Status": order_status,
        }])
        st.session_state.order_data = pd.concat(
            [st.session_state.order_data, new_order], ignore_index=True
        )
        st.success(f"Added item '{product}' to Order {order_id}!")
        st.rerun()

  st.markdown("---")
  st.subheader("📋 All Active Orders & Line Items")

  if st.session_state.order_data.empty:
    st.info("No active orders found.")
  else:
    st.dataframe(st.session_state.order_data, use_container_width=True)

    # Conversion & Management Section
    st.markdown("#### 🔄 Convert Entire Order to Shipping Details")
    col_conv1, col_conv2 = st.columns(2)

    with col_conv1:
      unique_orders = st.session_state.order_data["Order ID"].unique().tolist()
      selected_order = st.selectbox(
          "Select Order ID to Convert into Container Shipment:", unique_orders
      )

    with col_conv2:
      st.write("")
      st.write("")
      convert_button = st.button("Convert Order to Container Shipment ➡️")

    if convert_button:
      matching_items = st.session_state.order_data[
          st.session_state.order_data["Order ID"] == selected_order
      ]

      if not matching_items.empty:
        st.session_state.order_data.loc[
            st.session_state.order_data["Order ID"] == selected_order,
            "Order Status",
        ] = "Converted to Shipment"

        dummy_container_no = f"CONT-{selected_order}"

        new_shipments = []
        for _, row in matching_items.iterrows():
          exists = (
              (
                  st.session_state.container_data["Linked Order ID"]
                  == selected_order
              )
              & (
                  st.session_state.container_data["Product Description"]
                  == row["Product Description"]
              )
          ).any()

          if not exists:
            new_shipments.append({
                "Container Number": dummy_container_no,
                "Vessel Name": "TBD",
                "Product Description": row["Product Description"],
                "Quantity": row["Quantity"],
                "Bill of Lading (B/L)": "Pending",
                "ACD Status": "Pending",
                "COO Status": "Pending",
                "SOB Date": "Pending",
                "ETA": "2026-06-01",
                "Status": "In Transit",
                "Compliance Alert": f"Converted from Order {selected_order}",
                "Linked Order ID": selected_order,
            })

        if new_shipments:
          df_new_ships = pd.DataFrame(new_shipments)
          st.session_state.container_data = pd.concat(
              [st.session_state.container_data, df_new_ships], ignore_index=True
          )
          st.success(
              f"Successfully converted Order {selected_order} ({len(new_shipments)}"
              f" line items) into Container Shipment {dummy_container_no}!"
          )
          st.rerun()
        else:
          st.warning(
              "These line items have already been converted to shipments."
          )

# ==========================================
# TAB 2: CONTAINER SHIPPING & COMPLIANCE
# ==========================================
with tab_containers:
  st.subheader("🚢 Container Shipping & Compliance Tracker")

  # Search Filter
  search_query = st.text_input(
      "🔍 Search by Container, Vessel, Product, B/L, or Order ID:", value=""
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
        | df_containers["Bill of Lading (B/L)"]
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

  st.markdown("---")

  # Management Controls: Update Compliance/Shipping Data & Delete
  col_update, col_delete = st.columns(2)

  with col_update:
    st.subheader("✏️ Update Compliance & Shipping Details")
    if not st.session_state.container_data.empty:
      container_indices = st.session_state.container_data.index.tolist()

      def format_container_dropdown(idx):
        row = st.session_state.container_data.loc[idx]
        return (
            f"Row {idx}: {row['Container Number']} ({row['Product Description']})"
        )

      selected_idx = st.selectbox(
          "Select Shipment Item to Edit:",
          container_indices,
          format_func=format_container_dropdown,
      )

      current_row = st.session_state.container_data.loc[selected_idx]

      with st.form("update_container_form"):
        up_vessel = st.text_input(
            "Vessel Name", value=str(current_row["Vessel Name"])
        )
        up_bl = st.text_input(
            "Bill of Lading (B/L)",
            value=str(current_row["Bill of Lading (B/L)"]),
        )
        up_acd = st.text_input(
            "ACD Status / Ref", value=str(current_row["ACD Status"])
        )
        up_coo = st.text_input(
            "COO Status / Ref", value=str(current_row["COO Status"])
        )
        up_sob = st.text_input(
            "SOB (Shipped on Board) Date", value=str(current_row["SOB Date"])
        )
        up_eta = st.text_input("ETA", value=str(current_row["ETA"]))

        up_status = st.selectbox(
            "Shipment Status",
            ["In Transit", "Customs Hold", "Cleared", "Delivered"],
            index=(
                [
                    "In Transit",
                    "Customs Hold",
                    "Cleared",
                    "Delivered",
                ].index(current_row["Status"])
                if current_row["Status"]
                in ["In Transit", "Customs Hold", "Cleared", "Delivered"]
                else 0
            ),
        )

        up_alert = st.text_input(
            "Compliance Alert / Notes",
            value=str(current_row["Compliance Alert"]),
        )

        save_update = st.form_submit_button("Save Shipment Updates")

        if save_update:
          st.session_state.container_data.loc[selected_idx, "Vessel Name"] = (
              up_vessel
          )
          st.session_state.container_data.loc[
              selected_idx, "Bill of Lading (B/L)"
          ] = up_bl
          st.session_state.container_data.loc[selected_idx, "ACD Status"] = (
              up_acd
          )
          st.session_state.container_data.loc[selected_idx, "COO Status"] = (
              up_coo
          )
          st.session_state.container_data.loc[selected_idx, "SOB Date"] = up_sob
          st.session_state.container_data.loc[selected_idx, "ETA"] = up_eta
          st.session_state.container_data.loc[selected_idx, "Status"] = (
              up_status
          )
          st.session_state.container_data.loc[
              selected_idx, "Compliance Alert"
          ] = up_alert
          st.success("Shipment and compliance details updated successfully!")
          st.rerun()
    else:
      st.caption("No shipments available to update.")

  with col_delete:
    st.subheader("🗑️ Delete Shipment")
    if not st.session_state.container_data.empty:
      cont_list = st.session_state.container_data["Container Number"].tolist()
      selected_cont_to_delete = st.selectbox(
          "Select Container Number to Remove:",
          cont_list,
          key="delete_cont_select",
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
        label="📥 Export Container & Compliance Tracker to CSV",
        data=csv_data,
        file_name="container_compliance_tracker.csv",
        mime="text/csv",
    )