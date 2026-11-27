import { Controller, Get, Query } from '@nestjs/common';
import { ApiOperation, ApiBadRequestResponse } from '@nestjs/swagger';
import { AppService } from './app.service';
import { SampleQueryDto } from './common/dto/sample-query.dto';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }

  @Get('sample')
  @ApiOperation({
    summary: 'Test pagination, filtering and DTO validation',
  })
  @ApiBadRequestResponse({
    description: 'Invalid query parameters',
  })
  getSample(@Query() query: SampleQueryDto) {
    const records = [
      { id: 1, name: 'Sample Alpha' },
      { id: 2, name: 'Sample Beta' },
      { id: 3, name: 'Sample Gamma' },
      { id: 4, name: 'Sample Delta' },
      { id: 5, name: 'Sample Epsilon' },
    ];

    const { page, limit, search } = query;

    const filtered = search
      ? records.filter((record) =>
          record.name.toLowerCase().includes(search.toLowerCase()),
        )
      : records;

    const offset = (page - 1) * limit;

    return {
      data: filtered.slice(offset, offset + limit),
      meta: {
        page,
        limit,
        total: filtered.length,
        totalPages: Math.ceil(filtered.length / limit),
      },
    };
  }
}