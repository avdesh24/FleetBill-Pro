import streamlit as st
import pandas as pd
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

st.set_page_config(page_title="Vehicle Billing System", layout="wide")

st.title("Vehicle Billing System")

# FILE UPLOAD
uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx", "xls"]
)

if uploaded_file is not None:

    # Read Excel
    df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip().str.lower()

    df = df[
        ['vehicle reg no', 'city', 'sub vendor rate']
    ]

    st.success("File Loaded Successfully")

    # VEHICLE SELECTION
    vehicles = df['vehicle reg no'].unique()

    selected_vehicle = st.selectbox(
        "Select Vehicle",
        vehicles
    )

    vehicle_data = df[
        df['vehicle reg no'] == selected_vehicle
    ]

    # TRIP SUMMARY
    trip_summary = (
        vehicle_data
        .groupby(['city', 'sub vendor rate'])
        .size()
        .reset_index(name='trip_count')
    )

    trip_summary['amount'] = (
        trip_summary['sub vendor rate']
        * trip_summary['trip_count']
    )

    total_trips = trip_summary['trip_count'].sum()
    total_amount = trip_summary['amount'].sum()

    total_row = pd.DataFrame({
        'city': ['TOTAL'],
        'sub vendor rate': [''],
        'trip_count': [total_trips],
        'amount': [total_amount]
    })

    trip_summary_display = pd.concat(
        [trip_summary, total_row],
        ignore_index=True
    )

    st.subheader("Trip Summary")

    st.dataframe(
        trip_summary_display,
        use_container_width=True
    )

    # MONTH
    month = st.text_input(
        "Month",
        placeholder="June 2026"
    )

    # CHARGES
    st.subheader("Charges")

    col1, col2, col3 = st.columns(3)

    with col1:
        penalty = st.number_input(
            "Penalty",
            value=0.0
        )

        office_charge = st.number_input(
            "Office Charge",
            value=0.0
        )

    with col2:
        mcd = st.number_input(
            "MCD",
            value=0.0
        )

        gps = st.number_input(
            "GPS",
            value=0.0
        )

    with col3:
        tds = st.number_input(
            "TDS",
            value=0.0
        )

        toll_tax = st.number_input(
            "Toll Tax",
            value=0.0
        )

    # PAYMENT SUMMARY
    final_payable_amount = (
        total_amount
        + mcd
        + toll_tax
        - penalty
        - office_charge
        - gps
        - tds
    )

    payment_summary = pd.DataFrame({
        'Particular': [
            'Total Amount',
            'MCD',
            'Toll Tax',
            'Penalty',
            'Office Charge',
            'GPS',
            'TDS',
            'Final Payable Amount'
        ],
        'Amount': [
            total_amount,
            mcd,
            toll_tax,
            penalty,
            office_charge,
            gps,
            tds,
            final_payable_amount
        ]
    })

    st.subheader("Payment Summary")

    st.dataframe(
        payment_summary,
        use_container_width=True
    )

    st.metric(
        "Final Payable Amount",
        f"₹ {final_payable_amount:,.2f}"
    )

    # PDF GENERATION
    if st.button("Generate PDF"):

        pdf_file = (
            f"{selected_vehicle}_{month}_Bill.pdf"
        )

        doc = SimpleDocTemplate(
            pdf_file,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=22,
            spaceAfter=20
        )

        elements = []

        elements.append(
            Paragraph(
                "VEHICLE BILLING REPORT",
                title_style
            )
        )

        info_data = [[
            f"Vehicle No: {selected_vehicle}",
            f"Month: {month}"
        ]]

        info_table = Table(
            info_data,
            colWidths=[250, 250]
        )

        info_table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,-1),colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold')
        ]))

        elements.append(info_table)
        elements.append(Spacer(1,20))

        trip_data = (
            [trip_summary_display.columns.tolist()]
            + trip_summary_display.values.tolist()
        )

        trip_table = Table(
            trip_data,
            colWidths=[130,130,130,130]
        )

        trip_table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('ALIGN',(0,0),(-1,-1),'CENTER')
        ]))

        elements.append(
            Paragraph(
                "<b>Trip Summary</b>",
                styles["Heading2"]
            )
        )

        elements.append(trip_table)
        elements.append(Spacer(1,20))

        payment_data = (
            [payment_summary.columns.tolist()]
            + payment_summary.values.tolist()
        )

        payment_table = Table(
            payment_data,
            colWidths=[260,260]
        )

        payment_table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.darkgreen),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('ALIGN',(0,0),(-1,-1),'CENTER')
        ]))

        elements.append(
            Paragraph(
                "<b>Payment Summary</b>",
                styles["Heading2"]
            )
        )

        elements.append(payment_table)

        doc.build(elements)

        st.success("PDF Generated Successfully")

        with open(pdf_file, "rb") as file:
            st.download_button(
                label="Download PDF",
                data=file,
                file_name=pdf_file,
                mime="application/pdf"
            )