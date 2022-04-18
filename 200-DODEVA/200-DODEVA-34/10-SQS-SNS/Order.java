package com.amazonaws.lab;
// Copyright 2017 Amazon Web Services, Inc. or its affiliates. All rights reserved.

// The Order class is a POJO used to hold order information
public class Order {
	private int orderId;
	private String orderDate;
	private String orderDetails;
	private String senderId;
	private String sentTimestamp;

	public Order() {
	}

	public Order(int orderId, String orderDate, String orderDetails) {
		this.orderId = orderId;
		this.orderDate = orderDate;
		this.orderDetails = orderDetails;
	}

	public int getOrderId() {
		return orderId;
	}

	public void setOrderId(int orderId) {
		this.orderId = orderId;
	}

	public String getOrderDate() {
		return orderDate;
	}

	public void setOrderDate(String orderDate) {
		this.orderDate = orderDate;
	}

	public String getOrderDetails() {
		return orderDetails;
	}

	public void setOrderDetails(String orderDetails) {
		this.orderDetails = orderDetails;
	}

	public String getSenderId() {
		return senderId;
	}

	public void setSenderId(String senderId) {
		this.senderId = senderId;
	}

	public String getSentTimestamp() {
		return sentTimestamp;
	}

	public void setSentTimestamp(String sentTimestamp) {
		this.sentTimestamp = sentTimestamp;
	}

	public String toString() {
		String format = "Order id: %d,%n senderId: %s,%n sentTimestamp: %s,%n orderDate: %s,%n orderDetails: %s%n";
		String orderStr = String.format(format, orderId, senderId, sentTimestamp, orderDate, orderDetails);
		return orderStr;
	}
}
