
import {
    ArgumentsHost,
    BadRequestException,
    NotFoundException,
} from '@nestjs/common';

import { HttpExceptionFilter } from './http-exception.filter';

describe('HttpExceptionFilter', () => {
    let filter: HttpExceptionFilter;

    beforeEach(() => {
        filter = new HttpExceptionFilter();
    });

    it('should return a standardized 404 error response', () => {
        const request = {
            url: '/api/v1/projects/100',
        };

        const response = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn(),
        };

        const host = {
            switchToHttp: () => ({
                getRequest: () => request,
                getResponse: () => response,
            }),
        } as unknown as ArgumentsHost;

        const exception = new NotFoundException(
            'Project not found',
        );

        filter.catch(exception, host);

        expect(response.status).toHaveBeenCalledWith(404);

        expect(response.json).toHaveBeenCalledWith(
            expect.objectContaining({
                success: false,
                statusCode: 404,
                message: 'Project not found',
                error: 'Not Found',
                timestamp: expect.any(String),
                path: '/api/v1/projects/100',
            }),
        );
    });
    it('should return a standardized 400 error response', () => {
        const request = {
            url: '/api/v1/projects',
        };

        const response = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn(),
        };

        const host = {
            switchToHttp: () => ({
                getRequest: () => request,
                getResponse: () => response,
            }),
        } as unknown as ArgumentsHost;

        const exception = new BadRequestException(
            'Project name is required',
        );

        filter.catch(exception, host);

        expect(response.status).toHaveBeenCalledWith(400);

        expect(response.json).toHaveBeenCalledWith(
            expect.objectContaining({
                success: false,
                statusCode: 400,
                message: 'Project name is required',
                error: 'Bad Request',
                timestamp: expect.any(String),
                path: '/api/v1/projects',
            }),
        );
    });
    it('should preserve multiple validation messages', () => {
        const request = {
            url: '/api/v1/projects',
        };

        const response = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn(),
        };

        const host = {
            switchToHttp: () => ({
                getRequest: () => request,
                getResponse: () => response,
            }),
        } as unknown as ArgumentsHost;

        const exception = new BadRequestException({
            message: [
                'Project name should not be empty',
                'Project name must be a string',
            ],
            error: 'Bad Request',
            statusCode: 400,
        });

        filter.catch(exception, host);

        expect(response.json).toHaveBeenCalledWith(
            expect.objectContaining({
                success: false,
                statusCode: 400,
                message: [
                    'Project name should not be empty',
                    'Project name must be a string',
                ],
                error: 'Bad Request',
                timestamp: expect.any(String),
                path: '/api/v1/projects',
            }),
        );
    }); it('should use the exception message when response has no message property', () => {
        const request = {
            url: '/api/v1/projects',
        };

        const response = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn(),
        };

        const host = {
            switchToHttp: () => ({
                getRequest: () => request,
                getResponse: () => response,
            }),
        } as unknown as ArgumentsHost;

        const exception = new BadRequestException({
            error: 'Bad Request',
            statusCode: 400,
        });

        filter.catch(exception, host);

        expect(response.json).toHaveBeenCalledWith(
            expect.objectContaining({
                success: false,
                statusCode: 400,
                message: exception.message,
                error: 'Bad Request',
                timestamp: expect.any(String),
                path: '/api/v1/projects',
            }),
        );
    }); it('should return a standardized 500 response for unexpected errors', () => {
        const request = {
            url: '/api/v1/projects',
        };

        const response = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn(),
        };

        const host = {
            switchToHttp: () => ({
                getRequest: () => request,
                getResponse: () => response,
            }),
        } as unknown as ArgumentsHost;

        const exception = new Error(
            'Database connection failed',
        );

        filter.catch(exception, host);

        expect(response.status).toHaveBeenCalledWith(500);

        expect(response.json).toHaveBeenCalledWith(
            expect.objectContaining({
                success: false,
                statusCode: 500,
                message: 'Internal server error',
                error: 'Internal Server Error',
                timestamp: expect.any(String),
                path: '/api/v1/projects',
            }),
        );
    });
});
