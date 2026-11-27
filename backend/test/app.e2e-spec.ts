import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import request from 'supertest';
import { App } from 'supertest/types';
import { AppModule } from './../src/app.module';
import { HttpExceptionFilter } from './../src/common/filters/http-exception.filter';

describe('AppController (e2e)', () => {
  let app: INestApplication<App>;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();

    app.setGlobalPrefix('api');

    app.useGlobalFilters(new HttpExceptionFilter());

    app.useGlobalPipes(
      new ValidationPipe({
        whitelist: true,
        forbidNonWhitelisted: true,
        transform: true,
      }),
    );

    await app.init();
  });

  it('/api (GET)', () => {
    return request(app.getHttpServer())
      .get('/api')
      .expect(200)
      .expect('Hello World!');
  });

  it('should return paginated records', () => {
    return request(app.getHttpServer())
      .get('/api/sample?page=1&limit=2')
      .expect(200)
      .expect({
        data: [
          { id: 1, name: 'Sample Alpha' },
          { id: 2, name: 'Sample Beta' },
        ],
        meta: {
          page: 1,
          limit: 2,
          total: 5,
          totalPages: 3,
        },
      });
  });

  it('should filter records by search text', () => {
    return request(app.getHttpServer())
      .get('/api/sample?search=alpha')
      .expect(200)
      .expect({
        data: [{ id: 1, name: 'Sample Alpha' }],
        meta: {
          page: 1,
          limit: 10,
          total: 1,
          totalPages: 1,
        },
      });
  });

  it('should reject an invalid page number', () => {
    return request(app.getHttpServer())
      .get('/api/sample?page=-1')
      .expect(400)
      .expect(({ body }) => {
        expect(body.success).toBe(false);
        expect(body.statusCode).toBe(400);
        expect(body.message).toContain('page must not be less than 1');
      });
  });

  it('should reject a limit greater than 100', () => {
    return request(app.getHttpServer())
      .get('/api/sample?limit=101')
      .expect(400);
  });

  it('should reject unknown query parameters', () => {
    return request(app.getHttpServer())
      .get('/api/sample?unknown=value')
      .expect(400);
  });

  afterEach(async () => {
    await app.close();
  });
});