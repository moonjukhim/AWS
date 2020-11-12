
let response;
var fs = require('fs');
var filename;

/**
 *
 * Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
 * @param {Object} event - API Gateway Lambda Proxy Input Format
 *
 * Context doc: https://docs.aws.amazon.com/lambda/latest/dg/nodejs-prog-model-context.html 
 * @param {Object} context
 *
 * Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
 * @returns {Object} object - API Gateway Lambda Proxy Output Format
 * 
 */
exports.lambdaHandler = async (event, context) => {
    try {
        var foo = 'hello';
        filename = "./lab4b.html";

        var contents = fs.readFileSync(filename, 'utf8');

        response = {
            'statusCode': 200,
            'headers': {
                "Content-Type": "text/html; charset=utf-8"
            },
            'body': contents
        };
    } catch (err) {
        console.log(err);
        return err;
    }

    return response;
};
