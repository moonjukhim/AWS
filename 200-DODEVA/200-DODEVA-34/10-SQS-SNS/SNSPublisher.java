package com.amazonaws.lab;
// Copyright 2017 Amazon Web Services, Inc. or its affiliates. All rights reserved.

import com.amazonaws.services.sns.AmazonSNSClient;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

// The SNSPublisher class publishes messages to SNS topics
public class SNSPublisher {

	// TODO 1: Set ARN for SNS topic for email messages
	private static final String TOPIC_ARN_EMAIL = "<Email-SNS-Topic-ARN>";

	// TODO 2: Set ARN for SNS topic for order messages
	private static final String TOPIC_ARN_ORDER = "<Order-SNS-Topic-ARN>";

	private static final String EMAIL_SUBJECT = "Status of pharmaceuticals order.";
	private static final String EMAIL_MESSAGE = "Your pharmaceutical supplies will be shipped 5 business days from the date of order.";
	private static final String ORDER_DETAILS = "Ibuprofen, Acetaminophen";

	public static final int NUM_MESSAGES = 10;

	private static AmazonSNSClient snsClient = null;

	public static void main(String[] args) throws Exception {
		SNSPublisher snsPublisher = new SNSPublisher();
		snsPublisher.init();
		snsPublisher.publishMessages();
	}

	private void init() throws Exception {
		createSNSClient();
	}

	private void publishMessages() throws Exception {
		publishEmailMessage();
		publishOrderMessages();
	}

	private void publishOrderMessages() throws JsonProcessingException {
		ObjectMapper mapper = new ObjectMapper();
		Order order = null;
		String jsonOrder = null; // Order in JSON format.
		for (int i = 1; i < (NUM_MESSAGES + 1); i++) {
			order = new Order(i, "2015/10/" + i, ORDER_DETAILS);
			System.out.println("Publishing order to SNS topic: " + order);
			jsonOrder = convertOrderToJSON(mapper, order);
			publishOrder(jsonOrder);
		}
	}

	/**
	 * Create an instance of the AmazonSNSClient class
	 *
	 * @param credentials
	 *            AWS Credentials
	 */
	private static void createSNSClient() {
		// TODO 3: Replace the solution with your own code
		snsClient = Solution.createSNSClient(snsClient);
	}

	/** Publish a message to the SNS topic for email messages */
	private static void publishEmailMessage() {
		// TODO 4: Replace the solution with your own code
		Solution.publishEmailMessage(snsClient, TOPIC_ARN_EMAIL, EMAIL_MESSAGE, EMAIL_SUBJECT);
	}

	/**
	 * Convert the order to JSON format
	 *
	 * @param mapper
	 *            Object mapper
	 * @param order
	 *            The order
	 * @return The order in JSON format
	 */
	private static String convertOrderToJSON(ObjectMapper mapper, Order order) {
		// TODO 5: Replace the solution with your own code
		return Solution.convertOrderToJSON(mapper, order);
	}

	/**
	 * Publish the JSON-formatted order to the SNS topic for orders.
	 *
	 * @param jsonOrder
	 *            The order in JSON format
	 */
	private static void publishOrder(String jsonOrder) {
		// TODO 6: Replace the solution with your own code
		Solution.publishOrder(snsClient, TOPIC_ARN_ORDER, jsonOrder);
	}
}
