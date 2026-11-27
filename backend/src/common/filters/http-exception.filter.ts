
import {
    ArgumentsHost,
    Catch,
    ExceptionFilter,
    HttpException,
    HttpStatus,
} from '@nestjs/common';

@Catch()
export class HttpExceptionFilter
    implements ExceptionFilter {
    catch(exception: unknown, host: ArgumentsHost) {
        const ctx = host.switchToHttp();

        const request = ctx.getRequest();
        const response = ctx.getResponse();

        const isHttpException = exception instanceof HttpException;

        const statusCode = isHttpException
            ? exception.getStatus()
            : HttpStatus.INTERNAL_SERVER_ERROR;

        let message: string | string[];

        if (!isHttpException) {
            message = 'Internal server error';
        } else {
            const exceptionResponse = exception.getResponse();

            if (typeof exceptionResponse === 'string') {
                message = exceptionResponse;
            } else if (
                typeof exceptionResponse === 'object' &&
                exceptionResponse !== null &&
                'message' in exceptionResponse
            ) {
                const responseMessage = exceptionResponse.message;

                message =
                    typeof responseMessage === 'string' ||
                        (Array.isArray(responseMessage) &&
                            responseMessage.every(
                                (item) => typeof item === 'string',
                            ))
                        ? responseMessage
                        : exception.message;
            } else {
                message = exception.message;
            }
        }
        const errorName = HttpStatus[statusCode];

        const error = errorName
            ? errorName
                .split('_')
                .map(
                    (word) =>
                        word.charAt(0) + word.slice(1).toLowerCase(),
                )
                .join(' ')
            : 'Internal Server Error';
        response.status(statusCode).json({
            success: false,
            statusCode,
            message,
            error,
            timestamp: new Date().toISOString(),
            path: request.url,
        });
    }
}
